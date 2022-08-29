from math import comb
import random
import traceback 
import PySimpleGUI as sg
import logging, time, threading

from data_management.model import AssemblyStep, Failure, Measurement
from data_management import data_controller, data_transformation

from hw_interface.motor_controller import RebelAxisController
from hw_interface.definitions import Exception_Controller_No_CAN_ID, Exception_PCAN_Connection_Failed
from hw_interface import current_limits

from gui.definitions import KeyDefs, LayoutPageKeys
from gui.definitions import TransmissionConfigHelper, TransmissionSize
from gui.helper_functions import can_connection_functions
from gui.pages import main_layout
from gui.pages import get_headline_for_index, get_page_keys, get_page_key_for_index,get_assembly_step_for_page_index
from gui.plotting import GraphPlotter


logFormatter = logging.Formatter("'%(asctime)s - %(message)s")
logger = logging.getLogger("start_app")
logger.setLevel(logging.DEBUG)

fileHandler = logging.FileHandler("gui.log", mode="w")
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)

consolerHandler = logging.StreamHandler()
consolerHandler.setFormatter(logFormatter)
logger.addHandler(consolerHandler)


#######################
### FUNCTIONS  ########
#######################

def radio_size_is_clicked(event, values, size:TransmissionSize):
    transmission_config.set_size(size)
    if size == TransmissionSize.size_80:
        window[KeyDefs.CHECKBOX_HAS_BRAKE].update(disabled=True)
    else:
        window[KeyDefs.CHECKBOX_HAS_BRAKE].update(disabled=False)


def checkbox_has_brake_clicked(event, values):
    transmission_config.set_brake_flag(values[event])


def checkbox_has_encoder_clicked(event, values):
    transmission_config.set_encoder_flag(values[event])
 


# Software update dummy
def perform_software_update(event, values):
    btn = window[KeyDefs.BTN_SOFTWARE_UPDATE]
    btn.update(disabled=True)
    threading.Thread(target=perform_software_update_thread, args=(window, controller), daemon=True ).start()

def perform_software_update_thread(window, controller):
    for i in range(1,101):
        time.sleep(.1)
        window.write_event_value(KeyDefs.SOFTWARE_UPDATE_FEEDBACK, i/10)
    window.write_event_value(KeyDefs.SOFTWARE_UPDATE_DONE, None)
    

def check_moveability(event, values):
    ...
    logger.info("check_moveability button clicked")
    controller.reach_moveability()


# VELOCITY MODE

def start_velocity_mode(event, values, controller:RebelAxisController):

    step = get_assembly_step_for_page_index(current_page_index)
    # assembly = data_controller.get_or_create_assembly_for_assembly_step(step)
    assembly = data_controller.get_assembly_from_current_transmission(step)
    data_controller.create_measurement(assembly)

    global thread_graph_updater
    thread_graph_updater = threading.Thread(target=graph_update_cycle, args=(window, controller, ), daemon=True)
    thread_graph_updater.start()

    # definition of stop-function that is invoked after the movement has stopped (e.g. duration is reached)
    stop_func = lambda: window.write_event_value(KeyDefs.FINISHED_VELO_STOP_GRAPH_UPDATING, "Data")
    controller.start_movement_velocity_mode(velocity=10, duration=3, invoke_stop_function = stop_func)


def stop_velocity_mode(event, values, controller:RebelAxisController):
    controller.stop_movement_velocity_mode()
    thread_graph_updater.do_plot = False


def graph_update_cycle(window:sg.Window, controller:RebelAxisController):
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

            window.write_event_value(KeyDefs.UPDATE_GRAPH, "DATA")



def update_graph(event, values):
    """Updates graph. Gets called from a thread running graph_update_cycle()."""
    page_key = get_page_key_for_index(current_page_index)
    
    plotter = plotters[page_key]

    data = data_controller.get_plot_data_for_current_measurement()
    x_data, y_data = zip(*data)
    plotter.plot_data(x_data, y_data)


def stop_graph_update(event, values):
    """
    Gets called when the movement is finished and therefore the plotting update thread can be finished also.
    Instance of 'window' is passed to motor_controller which then invokes event '-KEY_FINISHED_VELO_STOP_GRAPH_UPDATING-'.
    """
    logger.info("#"*10)
    logger.info("Velocity finished; Stop graph updating thread!")

    global thread_graph_updater
    thread_graph_updater.do_plot = False

    # page_key = get_page_key_for_index(current_page_index)

    # Update min/ max fields in gui
    text_field = window[(KeyDefs.TEXT_MIN_MAX_CURRENT_VALUES, LayoutPageKeys.layout_assembly_step_1_page)]
    measurement = data_controller.get_current_measurement_instance()
    min_val, max_val, mean_val = measurement.min_current, measurement.max_current, measurement.mean_current

    text_field.update(f"Min current: {min_val} ||| Max. current: {max_val} || Mean current: {mean_val}")

    predict_failure(measurement)



def predict_failure(measurement: Measurement):
    """Tries to predict < Indicator > (e.g. Overcurrent) based on currently measurement taken. Gets called after graph updating has stopped. """

    logger.info("#"*10)
    logger.info("predict_failure")

    # global combo_indicators
    assembly_step = get_assembly_step_for_page_index(current_page_index)
    failures = data_controller.get_failures_list_for_assembly_step(assembly_step)

    f = failures[0]
    global failure_selection 
    failure_selection = f

    window[KeyDefs.FRAME_FAILURE_DETECTION].update(visible=True)
    window[KeyDefs.COMBO_FAILURE_SELECT].update(values = failures, value=f)


### Selected Failure
def combo_failure_selection(event, values):
    f = values[event]
    logger.info("*"*10)
    logger.info(f"combo_failure_selection(): {f}")
    global failure_selection
    failure_selection = f
    

def btn_failure_selection_clicked(event, values):
    logger.info("*"*10)
    logger.info(f"btn_failure_selection_clicked: {failure_selection}")
    improvements = data_controller.get_improvements_for_failure(failure_selection)
    window[KeyDefs.LISTBOX_POSSIBLE_IMPROVEMENTS].update(improvements)
    window[KeyDefs.FRAME_POSSIBLE_IMPROVEMENTS].update(visible=True)


# selected improvement from list
def list_improvement_selected(event, values):
    logger.info("*"*10)
    selected_improvement = values[event][0]
    logger.info(f"list_improvement_selected: {selected_improvement}")

    global improvement_selection
    improvement_selection = selected_improvement
    

def btn_improvement_selection_clicked(event, values):
    logger.info("*"*10)
    logger.info(f"btn_improvement_selection_clicked: {improvement_selection}")

    


######################################################
# FUNCTIONS FOR ENABLING / DISABLING NAVIGATION BUTTONS
######################################################

def _update_headline(index):
    new_headline = get_headline_for_index(index)
    window["-headline-"].update(new_headline)
    

def _nav_next_page(event, values):
    """Called when user clicks on "Next"-Button. Manages hide/show of layouts etc."""
    global current_page_index

    _hide_current_page()

    current_page_index += 1
    _show_next_page()
    _disable_enable_nav_buttons()
   
    page_key = get_page_key_for_index(current_page_index)
   
    if page_key == LayoutPageKeys.layout_assembly_step_1_page:
        config = transmission_config.get_transmission_config()
        data_controller.create_transmission(config)
            
    elif page_key == LayoutPageKeys.layout_assembly_step_2_page:
        ...
    elif page_key == LayoutPageKeys.layout_assembly_step_3_page:
        ...
        

def _nav_previous_page(event, values):
    """Called when user clicks on "Previous"-Button. Manages hide/show of layouts etc."""
    global current_page_index
    _hide_current_page()

    current_page_index -= 1
    _show_next_page()
    _disable_enable_nav_buttons()


def _hide_current_page():
    global current_page_index
    current_page = window[get_page_keys()[current_page_index]]
    current_page.update(visible=False)
    # current_page.hide_row()

def _show_next_page():
    global current_page_index
    
    next_page = window[get_page_keys()[current_page_index]]
    next_page.update(visible=True)

    _update_headline(current_page_index)
    # next_page.unhide_row()

def _disable_enable_nav_buttons():
    
    btn_next = window[KeyDefs.BTN_NAV_NEXT_PAGE]
    btn_prev = window[KeyDefs.BTN_NAV_PREVIOUS_PAGE]

    btn_prev.update(disabled=False)
    btn_next.update(disabled=False)

    if current_page_index == 0:
        btn_prev.update(disabled=True)
    
    elif current_page_index == len(get_page_keys()) -1:
        btn_next(disabled=True)
 



#################
### MAIN ROUNTINE
#################

if __name__ == "__main__":
    window = sg.Window("ReBeL Getriebe Montage & Kalibrierung", main_layout, size=(1200,1000), finalize=True, location=(0,0))
    controller = None
    try:
        controller = RebelAxisController(verbose=False)
    except Exception_PCAN_Connection_Failed as e:
        print("Exception PCAN Connection Failed:", e)
        can_connection_functions.update_connect_btn_status("PCAN_HW_ERROR", window, controller)
    except Exception_Controller_No_CAN_ID:
        ...
        can_connection_functions.update_connect_btn_status("ERROR_NO_CAN_ID_FOUND", window, controller)

    transmission_config = TransmissionConfigHelper()
    current_limits = current_limits.load_config()
    
    thread_velocity = None
    thread_graph_updater = None

    current_page_index = 0

    failure_selection = None
    improvement_selection = None


    plotters = {
        l:GraphPlotter(window[(KeyDefs.CANVAS_GRAPH_PLOTTING, l)]) for l in get_page_keys()[1:]
    }

    for p in plotters.values():
        p.plot_data([],[])


    key_function_map = {
        KeyDefs.BTN_NAV_NEXT_PAGE: (_nav_next_page, dict()),
        KeyDefs.BTN_NAV_PREVIOUS_PAGE: (_nav_previous_page, dict()),

        KeyDefs.RADIO_BUTTON_80_CLICKED: (radio_size_is_clicked, dict(size=TransmissionSize.size_80)),
        KeyDefs.RADIO_BUTTON_105_CLICKED:( radio_size_is_clicked, dict(size=TransmissionSize.size_105)),

        KeyDefs.BTN_CONNECT_CAN: (lambda *args, **kwargs: can_connection_functions.connect_can(**kwargs),dict(controller=controller, window=window)),
        KeyDefs.BTN_SOFTWARE_UPDATE: (perform_software_update, dict()),

        KeyDefs.SOFTWARE_UPDATE_FEEDBACK: (lambda event, values: window[KeyDefs.PROGRESSBAR_SOFTWARE_UPDATE].update_bar(values.get(event)), dict()),
        KeyDefs.SOFTWARE_UPDATE_DONE : (lambda *args: window[KeyDefs.TEXT_SOFTWARE_UPDATE_STATUS_TEXT].update("Software upgedated") , dict()),

        KeyDefs.CHECKBOX_HAS_ENCODER: (lambda event, values: transmission_config.set_encoder_flag(values[event]), dict()),
        KeyDefs.CHECKBOX_HAS_BRAKE: (lambda event, values: transmission_config.set_brake_flag(values[event]), dict()),
        
        KeyDefs.BTN_CHECK_MOVEABILITY: (check_moveability, dict()),

        (KeyDefs.BTN_START_VELO_MODE, LayoutPageKeys.layout_assembly_step_1_page): (start_velocity_mode, dict(controller=controller)),
        (KeyDefs.BTN_STOP_VELO_MODE, LayoutPageKeys.layout_assembly_step_1_page): (stop_velocity_mode, dict(controller=controller)),
        
        (KeyDefs.BTN_START_VELO_MODE, LayoutPageKeys.layout_assembly_step_2_page): (start_velocity_mode, dict(controller=controller)),
        (KeyDefs.BTN_STOP_VELO_MODE, LayoutPageKeys.layout_assembly_step_2_page): (stop_velocity_mode, dict(controller=controller)),
        
        (KeyDefs.BTN_START_VELO_MODE, LayoutPageKeys.layout_assembly_step_3_page): (start_velocity_mode, dict(controller=controller)),
        (KeyDefs.BTN_STOP_VELO_MODE, LayoutPageKeys.layout_assembly_step_3_page): (stop_velocity_mode, dict(controller=controller)),
        
        KeyDefs.UPDATE_GRAPH: (update_graph, dict()),
        KeyDefs.FINISHED_VELO_STOP_GRAPH_UPDATING: (stop_graph_update, dict()),

        KeyDefs.COMBO_FAILURE_SELECT: (combo_failure_selection, dict()),
        KeyDefs.BTN_FAILURE_DETECTION: (btn_failure_selection_clicked, dict()),
        
        
        KeyDefs.LISTBOX_POSSIBLE_IMPROVEMENTS: (list_improvement_selected, dict()),
        KeyDefs.BTN_SELECT_IMPROVEMENT: (btn_improvement_selection_clicked, dict()),



    }
    # Event loop
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Exit'):
            controller.stop_movement()
            controller.shut_down()
            break

        try:
            func, args = key_function_map.get(event)
            func(event, values, **args)
        
        except KeyboardInterrupt:
            controller.stop_movement()
            controller.shut_down()
            break
        
        except TypeError as e:
            logger.error(f"WARNING: Missing event in 'key_functin_map': Event = {event} // values = {values.get(event)}")
            logger.error(traceback.format_exc())
        
        except Exception as e:
            logger.error(f"Error has occured while executing event: {event} | function name: {func.__name__}")
            logger.error(traceback.format_exc())
        

    window.close()