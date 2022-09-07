from concurrent.futures import thread
import threading
import logging
from data_management.model import AssemblyStep

import time
from gui.plotting import GraphPlotter
from hw_interface.motor_controller import RebelAxisController

from gui import pages

from data_management import data_controller, data_transformation

thread_graph_updater = None


logFormatter = logging.Formatter("'%(asctime)s - %(message)s")
logger = logging.getLogger("start_app")
logger.setLevel(logging.DEBUG)

fileHandler = logging.FileHandler("measurement.log", mode="w")
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)

consolerHandler = logging.StreamHandler()
consolerHandler.setFormatter(logFormatter)
logger.addHandler(consolerHandler)


def stop_current_thread():
    global thread_graph_updater
    thread_graph_updater.do_plot = False


def start_measurement(controller: RebelAxisController, assembly_step:AssemblyStep, stop_func, error_func,  plotter:GraphPlotter):
    assembly = data_controller.get_assembly_from_current_transmission(assembly_step)
    data_controller.create_measurement(assembly)

    global thread_graph_updater
    thread_graph_updater = threading.Thread(target=graph_update_cycle, args=(controller, plotter), daemon=True)
    thread_graph_updater.start()

    controller.start_movement_velocity_mode(
        velocity=10, 
        duration=3, 
        invoke_stop_function=lambda: stop_graph_update(stop_func), 
        invoke_error_function=lambda *args: cancel_graph_update(error_func, *args))





def graph_update_cycle(controller:RebelAxisController, plotter:GraphPlotter):
    """Runs in a thread, ever few seconds it's raising an event for the graphical main queue to trigger graph updating."""

    cur_thread = threading.current_thread()
    while getattr(cur_thread, 'do_plot', True):
        time.sleep(1)
        logger.warning("graph_update_cycle()")

        batch = controller.get_movement_cmd_reply_batch(batchsize=controller.frequency_hz)
        logger.info(f"Batch generated: len = {len(batch)}")

        if len(batch) > 10:
            mean_current, pos, millis = data_transformation.sample_data(batch)
            logger.info(f"Batch values: mean current = {mean_current} / middle position = {pos} / middle millis = {millis}")
            
            # send value to data controller for adding them into data base :)
            data_controller.create_data_point_to_current_measurement(mean_current, millis)
            data_controller.update_current_measurement_fields()

            update_graph(plotter)

def update_graph(plotter:GraphPlotter):
    ...
    data = data_controller.get_plot_data_for_current_measurement()
    x_data, y_data = zip(*data)
    plotter.plot_data(x_data, y_data)




def abort_movement(*args, controller:RebelAxisController, **kwargs):
    controller.stop_movement_velocity_mode()
    stop_current_thread()


def stop_graph_update(stop_func):
    """
    Gets called when the movement is finished and therefore the plotting update thread can be finished also.
    Instance of 'window' is passed to motor_controller which then invokes event '-KEY_FINISHED_VELO_STOP_GRAPH_UPDATING-'.
    """
    logger.info("#"*10)
    logger.info("Velocity finished; Stop graph updating thread!")

    stop_current_thread()

    measurement = data_controller.get_current_measurement_instance()
    # data_controller.update_current_measurement_fields()
    stop_func(measurement)


def cancel_graph_update(error_func, *args):
    """
    Gets called when due to an error the measurement has to be stopped/ aborted."""
    logger.info("#"*10)
    logger.info("cancel_graph_update()")

    stop_current_thread()
    error_func(*args)

    