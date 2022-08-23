import traceback 
import PySimpleGUI as sg
import logging, time, threading

from data_management.model import AssemblyStep
from data_management import data_controller, data_transformation

from hw_interface.motor_controller import RebelAxisController
from hw_interface.definitions import Exception_Controller_No_CAN_ID, Exception_PCAN_Connection_Failed

from gui.definitions import KeyDefs, LayoutPageKeys
from gui.definitions import TransmissionConfigHelper, TransmissionSize
from gui.helper_functions import can_connection_functions
from gui.pages import main_layout
from gui.pages import get_headline_for_index, get_page_keys, get_page_key_for_index
from gui.plotting import GraphPlotter


logFormatter = logging.Formatter("'%(asctime)s - %(message)s")
logger = logging.getLogger()
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
    

# VELOCITY MODE

def start_velocity_mode(event, values, controller:RebelAxisController):
    data_controller.create_measurement_to_current_assembly()

    global thread_graph_updater

    thread_graph_updater = threading.Thread(target=graph_update_cycle, args=(window, controller, ), daemon=True)
    thread_graph_updater.start()


    # definition of stop-function that is invoked after the movement has stopped (e.g. duration is reached)
    stop_func = lambda: window.write_event_value(KeyDefs.FINISHED_VELO_STOP_GRAPH_UPDATING, "Data")
    controller.start_movement_velocity_mode(duration=5, invoke_stop_function = stop_func)


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
            
            window.write_event_value(KeyDefs.UPDATE_GRAPH, dict(x=pos, y=mean_current))

            # send value to data controller for adding them into data base :)
            data_controller.create_data_point_to_current_measurement(mean_current, millis)
            data_controller.update_current_measurement_fields()




def update_graph(event, values, plotter:GraphPlotter):
    """Updates graph. Gets called from a thread running graph_update_cycle()."""
    d = values[event]
    x, y = d.get('x'), d.get('y')
    
    x_data.append(x)
    y_data.append(y)

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

    # Update min/ max fields in gui
    text_field = window[KeyDefs.TEXT_MIN_MAX_CURRENT_VALUES]
    measurement = data_controller.get_current_measurement_instance()
    min_val, max_val = measurement.min_current, measurement.max_current

    text_field.update(f"Min current: {min_val} ||| Max. current: {max_val}")




def create_transmission():
    logger.info(f"create_transmission() config: {transmission_config}")
    config = transmission_config.get_transmission_config()
    transmission = data_controller.create_transmission(config)
    assembly = data_controller.create_assembly(transmission, AssemblyStep.step_1_no_flexring)



######################################################
# FUNCTIONS FOR ENABLING / DISABLING NAVIGATION BUTTONS
######################################################

def _update_headline(index):
    new_headline = get_headline_for_index(index)
    window["-headline-"].update(new_headline)
    

def _nav_next_page(event, values):
    """Called when user clicks on "Next"-Button. Manages hide/show of layouts etc."""
    global current_page_index

    page_key = get_page_key_for_index(current_page_index)

    if page_key == LayoutPageKeys.layout_config_page:
        #invoke method on btn-next-click for config page
        ...
        create_transmission()

    elif page_key == LayoutPageKeys.layout_assembly_step_1_page:
        #invoke method on btn-next-click for assembly-step1-page
        ...
    
    _hide_current_page()

    current_page_index += 1
    _show_next_page()
    _disable_enable_nav_buttons()


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
    window = sg.Window("ReBeL Getriebe Montage & Kalibrierung", main_layout, size=(1200,800), finalize=True)
    controller = None
    try:
        controller = RebelAxisController(verbose=False)
    except Exception_PCAN_Connection_Failed as e:
        print("Exception PCAN Connection Failed:", e)
        can_connection_functions.update_connect_btn_status(status="PCAN_HW_ERROR")
    except Exception_Controller_No_CAN_ID:
        ...
        can_connection_functions.update_connect_btn_status(status="ERROR_NO_CAN_ID_FOUND")

    transmission_config = TransmissionConfigHelper()
    
    thread_velocity = None
    thread_graph_updater = None

    current_page_index = 0

    graph_plotter = GraphPlotter(window[KeyDefs.CANVAS_GRAPH_PLOTTING])
    graph_plotter.plot_data([], [])

    x_data, y_data = [],[]

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
        
        KeyDefs.BTN_START_VELO_MODE: (start_velocity_mode, dict(controller=controller)),
        KeyDefs.BTN_STOP_VELO_MODE: (stop_velocity_mode, dict(controller=controller)),
        KeyDefs.UPDATE_GRAPH: (update_graph, dict(plotter=graph_plotter)),
        KeyDefs.FINISHED_VELO_STOP_GRAPH_UPDATING: (stop_graph_update, dict())



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
        
        except Exception as e:
            logger.error(f"WARNING: Missing event in 'key_functin_map': Event = {event} // values = {values.get(event)}")
            logger.error(traceback.format_exc())
        

    window.close()