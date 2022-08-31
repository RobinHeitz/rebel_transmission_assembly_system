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
import gui.improvement_window as improvement_window

from gui import start_measurement



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
    """Invoked by Btn click: Start Measurement"""
    step = get_assembly_step_for_page_index(current_page_index)
    
    page_key = get_page_key_for_index(current_page_index)
    plotter = plotters[page_key]
    start_measurement.start_measurement(controller, step, measurement_finished, plotter)


def measurement_finished(m:Measurement):
    """Invoked by start_measurement.start_measurement. Callback function for updating gui elements based on finished measurement."""
    text_field = window[(KeyDefs.TEXT_MIN_MAX_CURRENT_VALUES, LayoutPageKeys.layout_assembly_step_1_page)]
    text_field.update(f"Min current: {m.min_current} ||| Max. current: {m.max_current} || Mean current: {m.mean_current}")
    predict_failure(m)



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
    # data_controller.create_failure_instance(failure_selection)
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
    # imp_instance = data_controller.create_improvement_instance(improvement_selection)
    improvement_window.improvement_window(controller, failure_selection, improvement_selection)
    

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
    window = sg.Window("ReBeL Getriebe Montage & Kalibrierung", main_layout, size=(1200,1000), finalize=True, location=(0,0),resizable=True)
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
        # (KeyDefs.BTN_STOP_VELO_MODE, LayoutPageKeys.layout_assembly_step_1_page): (stop_velocity_mode, dict(controller=controller)),
        (KeyDefs.BTN_STOP_VELO_MODE, LayoutPageKeys.layout_assembly_step_1_page): (start_measurement.abort_movement ,dict(controller=controller)),
        
        (KeyDefs.BTN_START_VELO_MODE, LayoutPageKeys.layout_assembly_step_2_page): (start_velocity_mode, dict(controller=controller)),
        # (KeyDefs.BTN_STOP_VELO_MODE, LayoutPageKeys.layout_assembly_step_2_page): (stop_velocity_mode, dict(controller=controller)),
        
        (KeyDefs.BTN_START_VELO_MODE, LayoutPageKeys.layout_assembly_step_3_page): (start_velocity_mode, dict(controller=controller)),
        # (KeyDefs.BTN_STOP_VELO_MODE, LayoutPageKeys.layout_assembly_step_3_page): (stop_velocity_mode, dict(controller=controller)),
        
        # KeyDefs.UPDATE_GRAPH: (update_graph, dict()),
        # KeyDefs.FINISHED_VELO_STOP_GRAPH_UPDATING: (stop_graph_update, dict()),

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
        elif callable(event):
            event()

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