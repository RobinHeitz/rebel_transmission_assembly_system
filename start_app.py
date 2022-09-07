import random
import traceback 
import PySimpleGUI as sg
import logging, time, threading

from sqlalchemy.orm.session import Session

import traceback

from data_management.model import AssemblyStep, Failure, FailureType, ImprovementInstance, Measurement
from data_management import data_controller, data_transformation

from hw_interface.motor_controller import RebelAxisController
from hw_interface.definitions import ExceptionPcanIllHardware, ExceptionPcanNoCanIdFound
from current_limits import get_current_limit_for_assembly_step

from gui.definitions import KeyDefs, LayoutPageKeys
from gui.definitions import TransmissionConfigHelper, TransmissionSize
from gui.helper_functions import can_connection_functions
from gui.pages import main_layout
from gui.pages import get_headline_for_index, get_page_keys, get_page_key_for_index,get_assembly_step_for_page_index
from gui.plotting import GraphPlotter
import gui.improvement_window as improvement_window

from gui import start_measurement

from logs.setup_logger import setup_logger
logger = setup_logger("start_app")


def function_prints(f):
    def wrap(*args, **kwargs):
        ...
        logger.info(f"--- {f.__name__}() called")
        return f(*args, **kwargs)
    return wrap


###################################################################
### FUNCTIONS FOR PERFORMING A CALLBACK-FUNCTION IN THE MAIN THREAD
###################################################################

@function_prints
def perform_callback_function_to_main_thread(func, *args):
    """Writes an event to window, which then calls a 'invoked_callback_in_main_thread' which again calls the attributed function with parameters."""
    window.write_event_value(KeyDefs.EVENT_CALLBACK_FUNCTION_MAIN_THREAD, [func, args])

@function_prints
def invoked_callback_in_main_thread(event, values):
    args = values[event]
    func = args[0]
    func(*args[1])



#################################
### TRANSMISSION CONFIG  ########
#################################
@function_prints
def radio_size_is_clicked(event, values, size:TransmissionSize):
    update_next_page_btn(next_page_is_allowed=True)
    transmission_config.set_size(size)
    if size == TransmissionSize.size_80:
        window[KeyDefs.CHECKBOX_HAS_BRAKE].update(disabled=True)
    else:
        window[KeyDefs.CHECKBOX_HAS_BRAKE].update(disabled=False)


@function_prints
def checkbox_has_brake_clicked(event, values):
    transmission_config.set_brake_flag(values[event])


@function_prints
def checkbox_has_encoder_clicked(event, values):
    transmission_config.set_encoder_flag(values[event])


###################
### CONNECT CAN ###
###################
@function_prints
def btn_connect_can(*args):
    """Btn 'Connect can' is clicked."""
    logger.debug(f"Controller: {controller} / can-id: {controller.can_id}")
    
    if controller.can_id != -1:
        logger.debug(f"CAN ID has been found: {hex(controller.can_id)}")
        window[KeyDefs.TEXT_CAN_CONNECTED_STATUS].update(f"Connected. CAN-ID: {hex(controller.can_id)}")
        window[KeyDefs.BTN_CONNECT_CAN].update(disabled=True)
    else:
        logger.debug("No can id available.")
        window[KeyDefs.TEXT_CAN_CONNECTED_STATUS].update(f"Searching for CAN-ID...")
        threading.Thread(target=search_for_can_id_thread, args=(window, controller), daemon=True).start()

@function_prints
def search_for_can_id_thread(window:sg.Window, controller:RebelAxisController):
    try:
        board_id = controller.find_can_id(timeout=2)
    except ExceptionPcanNoCanIdFound:
        window[KeyDefs.TEXT_CAN_CONNECTED_STATUS].update("Seems like no device is connected or Module Control is open?")
    else:
        window[KeyDefs.TEXT_CAN_CONNECTED_STATUS].update(f"Connected. CAN-ID: {hex(board_id)}")
        window[KeyDefs.BTN_CONNECT_CAN].update(disabled=True)



#############################
### BUTTON CHECK ERROR CODES:
#############################

@function_prints
def is_estop_error(*args):
    controller.cmd_reset_errors()
    controller.do_cycle()
    controller.cmd_reset_errors()
    controller.do_cycle()
    controller.cmd_velocity_mode(0)
    time.sleep(0.5)
    error_codes = controller.movement_cmd_errors
    logger.debug(f"current Error codes: {error_codes}")

    if "ESTOP" in error_codes:
        sg.popup("24V Versorgung fehlt","Dem Controller fehlt die 24V-Versorgung. Bitte das Kabel überprüfen.",)
        return True
    return False





########################
# Software update dummy
########################
@function_prints
def perform_software_update(event, values):
    btn = window[KeyDefs.BTN_SOFTWARE_UPDATE]
    btn.update(disabled=True)
    threading.Thread(target=perform_software_update_thread, args=(window, controller), daemon=True ).start()

@function_prints
def perform_software_update_thread(window, controller):
    for i in range(1,101):
        time.sleep(.1)
        window.write_event_value(KeyDefs.SOFTWARE_UPDATE_FEEDBACK, i/10)
    window.write_event_value(KeyDefs.SOFTWARE_UPDATE_DONE, None)
    

@function_prints
def check_moveability(event, values):
    controller.reach_moveability()

###############
# VELOCITY MODE
###############

@function_prints
def start_velocity_mode(event, values, controller:RebelAxisController):
    """Invoked by Btn click: Start Measurement"""
    _hide_failure_and_improvement_items()

    step = get_assembly_step_for_page_index(current_page_index)
    
    page_key = get_page_key_for_index(current_page_index)
    plotter = plotters[page_key]
    start_measurement.start_measurement(controller, step, measurement_finished_callback,measurement_error_callback ,plotter)


@function_prints
def measurement_finished_callback(m:Measurement):
    """Gets called from thread. To get this into main thread, call window.write_event_value."""
    # window.write_event_value(KeyDefs.EVENT_INITIAL_MEASUREMENT_FINISHED, m)
    perform_callback_function_to_main_thread(measurement_finished, m)



@function_prints
def measurement_error_callback(error):
    """This callback is called by controller instance, if motor can't move withe error code 'OC'"""
    perform_callback_function_to_main_thread(handle_error_while_measurement, error)


@function_prints
def handle_error_while_measurement(error):
    assembly_step = get_assembly_step_for_page_index(current_page_index)
    logger.info(f"Error code: {error} / assembly_step = {assembly_step}")
    session:Session = data_controller.create_session()
    
    failures = session.query(Failure).filter_by(assembly_step = assembly_step, failure_type = FailureType.overcurrent_not_moving).all()
    
    
    if len(failures) != 1: raise Exception("DataStruture is corrupt! There should be only 1 instance of failure for a given AssemblyStep with FailureType overcurrent_not_moving.")
    session.close()
    
    window[KeyDefs.TEXT_HIGH_CURRENT_FAILURE_DETECTED].update(f"Es wurde ein Fehler erkannt: {failures[0]}", text_color="red", visible=True)
    window[KeyDefs.COMBO_FAILURE_SELECT].update(values=failures, value=failures[0])
    change_combo_failures_visibility(False)
    show_improvements(failures[0])




@function_prints
def measurement_finished(m:Measurement):
    logger.error(f"measurement = {m} / id = {m.id}")
    """Invoked by start_measurement.start_measurement. Callback function for updating gui elements based on finished measurement."""
    text_field = window[(KeyDefs.TEXT_MIN_MAX_CURRENT_VALUES, LayoutPageKeys.layout_assembly_step_1_page)]
    text_field.update(f"Min current: {m.min_current} ||| Max. current: {m.max_current} || Mean current: {m.mean_current}", visible=True)
    predict_failure(m)




@function_prints
def predict_failure(measurement: Measurement):
    """Tries to predict < Indicator > (e.g. Overcurrent) based on currently measurement taken. Gets called after graph updating has stopped. """

    assembly_step = get_assembly_step_for_page_index(current_page_index)
    limit = get_current_limit_for_assembly_step(assembly_step)
    
    if measurement.max_current > limit:
        session:Session = data_controller.create_session()
        failures = session.query(Failure).filter_by(assembly_step = assembly_step, failure_type = FailureType.overcurrent).all()
        if len(failures) != 1: raise Exception("DataStruture is corrupt! There should be only 1 instance of failure for a given AssemblyStep with FailureType overcurrent.")
        session.close()
        window[KeyDefs.TEXT_HIGH_CURRENT_FAILURE_DETECTED].update(f"Es wurde ein Fehler erkannt: {failures[0]}", text_color="red", visible=True)
        window[KeyDefs.COMBO_FAILURE_SELECT].update(values=failures, value=failures[0])
        change_combo_failures_visibility(False)
        show_improvements(failures[0])

    else:
        answer  = sg.popup_yes_no("Strom ist nicht zu hoch", "Der Strom ist nicht zu hoch. Ist dir sonst noch ein Fehler aufgefallen?")
        if answer == "Yes":
            show_combo_failure_selection()
        elif answer == "No":
            update_next_page_btn(True)
        else:
            raise NotImplementedError("This Button Label is not checked against (yet)!")


@function_prints
def show_combo_failure_selection(*args, **kwargs):
    """Btn click: Fehler manuell detektieren. Shows Combo-Box of possible Failures."""
    assembly_step = get_assembly_step_for_page_index(current_page_index)
    failures = data_controller.sorted_failures_by_incidents(assembly_step)
        
    window[KeyDefs.FRAME_FAILURE_DETECTION].update(visible=True)
    window[KeyDefs.COMBO_FAILURE_SELECT].update(values=failures, value=failures[0])

    change_combo_failures_visibility(True)
    show_improvements(failures[0])

@function_prints
def combo_value_changes(event, values):
    """If combo's selected value changes, Possible Improvement Window should hide."""
    show_improvements(values[event])


@function_prints
def change_combo_failures_visibility(visible):
    t = window[KeyDefs.COL_FAILURE_SELECTION_CONTAINER]
    t.update(visible=visible)
        

@function_prints
def show_improvements(f:Failure, *args, **kwargs):
    """Shows Frame + Listbox with possible Improvements."""
    assembly_step = get_assembly_step_for_page_index(current_page_index)
    improvements = data_controller.get_improvements_for_failure(f, assembly_step, *args, **kwargs)
    
    if len(improvements) > 0:
        window[KeyDefs.FRAME_FAILURE_DETECTION].update(visible=True)
        window[KeyDefs.LISTBOX_POSSIBLE_IMPROVEMENTS].update(improvements, set_to_index=[0,])

    else:
        window[KeyDefs.FRAME_FAILURE_DETECTION].update(visible=False)
        sg.popup("Keine weitere Behebungsmaßnahme","Es ist keine weitere Fehlerbehebungsmaßnahme hinterlegt. Wenn du eine weiter findest, füge sie bitte hinzu. Solltest du den Fehler nicht finden können, ist das Getriebe Ausschuss.")


@function_prints
def btn_improvement_selection_clicked(event, values):
    selected_improvement = values[KeyDefs.LISTBOX_POSSIBLE_IMPROVEMENTS][0]
    selected_failure = values[KeyDefs.COMBO_FAILURE_SELECT]
    latest_measure = data_controller.get_current_measurement_instance()
    logger.info(f"btn_improvement_selection_clicked: {selected_improvement} | selected_failure = {selected_failure} | measurement = {latest_measure}")

    assembly_step = get_assembly_step_for_page_index(current_page_index)
    fail_instance, imp_instance = improvement_window.improvement_window(controller, current_transmission, selected_failure, selected_improvement, latest_measure, assembly_step)
    
    # for some reason; need to create anothger sesseion since this value is wrooong
    session = data_controller.create_session()
    imp_instance = session.query(ImprovementInstance).get(imp_instance.id)

    if imp_instance.successful == True:
        window[KeyDefs.FRAME_FAILURE_DETECTION].update(visible=False)
        update_next_page_btn(True)
    else:
        show_improvements(selected_failure)
        change_combo_failures_visibility(False)

    

@function_prints
def _hide_failure_and_improvement_items():
    window[KeyDefs.FRAME_FAILURE_DETECTION].update(visible=False)
    window[KeyDefs.TEXT_HIGH_CURRENT_FAILURE_DETECTED].update(visible=False)
    window[(KeyDefs.TEXT_MIN_MAX_CURRENT_VALUES, LayoutPageKeys.layout_assembly_step_1_page)].update(visible=False)
    

######################################################
# FUNCTIONS FOR ENABLING / DISABLING NAVIGATION BUTTONS
######################################################

@function_prints
def update_next_page_btn(next_page_is_allowed):
    btn = window[KeyDefs.BTN_NAV_NEXT_PAGE]
    if next_page_is_allowed == True:
        btn.update(button_color="green", disabled=False)
    else:
        btn.update(button_color="darkblue", disabled=True)



@function_prints
def _update_headline(index):
    new_headline = get_headline_for_index(index)
    window["-headline-"].update(new_headline)
    

@function_prints
def _nav_next_page(event, values):
    """Called when user clicks on "Next"-Button. Manages hide/show of layouts etc."""
    global current_page_index, current_transmission

    future_index = current_page_index + 1
    page_key = get_page_key_for_index(future_index)

    condition = condition_next_page_map.get(page_key)
    if condition():
        ...
        _hide_current_page()
        current_page_index = future_index
        _show_next_page()
        update_next_page_btn(False)
    


@function_prints
def _nav_previous_page(event, values):
    """Called when user clicks on "Previous"-Button. Manages hide/show of layouts etc."""
    global current_page_index
    _hide_current_page()

    current_page_index -= 1
    _show_next_page()
    update_next_page_btn(False)


@function_prints
def _hide_current_page():
    global current_page_index
    current_page = window[get_page_keys()[current_page_index]]
    current_page.update(visible=False)


@function_prints
def _show_next_page():
    global current_page_index
    
    next_page = window[get_page_keys()[current_page_index]]
    next_page.update(visible=True)

    _update_headline(current_page_index)


@function_prints
def _disable_enable_nav_buttons():
    # First version of nav button handling
    
    btn_next = window[KeyDefs.BTN_NAV_NEXT_PAGE]
    btn_prev = window[KeyDefs.BTN_NAV_PREVIOUS_PAGE]

    btn_prev.update(disabled=False)
    btn_next.update(disabled=False)

    if current_page_index == 0:
        btn_prev.update(disabled=True)
    
    elif current_page_index == len(get_page_keys()) -1:
        btn_next(disabled=True)
 


#################################
### CONDITIONS FOR NAVIGATION ###
#################################

@function_prints
def condition_leave_config_page():
    err = is_estop_error()
    if err:
        return False
        
    global current_transmission
    config = transmission_config.get_transmission_config()
    current_transmission = data_controller.create_transmission(config)
    return True



#################
### MAIN ROUNTINE
#################

if __name__ == "__main__":
    window = sg.Window("ReBeL Getriebe Montage & Kalibrierung", main_layout, size=(1200,1000), finalize=True, location=(0,0),resizable=True)
    
    # controller = None
    # thread_velocity = None
    # thread_graph_updater = None
    # current_transmission = None

    controller, thread_velocity, thread_graph_updater, current_transmission = (None, )*4

    try:
        controller = RebelAxisController(verbose=False)
        controller.connect()

    except ExceptionPcanIllHardware as e:
        logger.warning(e)
        window[KeyDefs.TEXT_CAN_CONNECTED_STATUS].update(str(e))
        window[KeyDefs.BTN_CONNECT_CAN].update(disabled=True)
    
    except ExceptionPcanNoCanIdFound as e:
        window[KeyDefs.TEXT_CAN_CONNECTED_STATUS].update(str(e))
        window[KeyDefs.BTN_CONNECT_CAN].update("Try Device again")

    
    transmission_config = TransmissionConfigHelper()
    

    current_page_index = 0



    plotters = {
        l:GraphPlotter(window[(KeyDefs.CANVAS_GRAPH_PLOTTING, l)]) for l in get_page_keys()[1:]
    }

    for p in plotters.values():
        p.plot_data([],[])

    window.maximize()

    condition_next_page_map = {
        LayoutPageKeys.layout_assembly_step_1_page: condition_leave_config_page,
        LayoutPageKeys.layout_assembly_step_2_page: lambda: print("Cond 2"),
        LayoutPageKeys.layout_assembly_step_3_page: lambda: print("Cond 3"),

    }


    key_function_map = {
        KeyDefs.BTN_NAV_NEXT_PAGE: (_nav_next_page, dict()),
        KeyDefs.BTN_NAV_PREVIOUS_PAGE: (_nav_previous_page, dict()),

        KeyDefs.RADIO_BUTTON_80_CLICKED: (radio_size_is_clicked, dict(size=TransmissionSize.size_80)),
        KeyDefs.RADIO_BUTTON_105_CLICKED:( radio_size_is_clicked, dict(size=TransmissionSize.size_105)),

        KeyDefs.BTN_CONNECT_CAN: (btn_connect_can, dict()),


        KeyDefs.BTN_SOFTWARE_UPDATE: (perform_software_update, dict()),
        KeyDefs.SOFTWARE_UPDATE_FEEDBACK: (lambda event, values: window[KeyDefs.PROGRESSBAR_SOFTWARE_UPDATE].update_bar(values.get(event)), dict()),
        KeyDefs.SOFTWARE_UPDATE_DONE : (lambda *args: window[KeyDefs.TEXT_SOFTWARE_UPDATE_STATUS_TEXT].update("Software upgedated") , dict()),

        KeyDefs.CHECKBOX_HAS_ENCODER: (lambda event, values: transmission_config.set_encoder_flag(values[event]), dict()),
        KeyDefs.CHECKBOX_HAS_BRAKE: (lambda event, values: transmission_config.set_brake_flag(values[event]), dict()),
        
        (KeyDefs.BTN_START_VELO_MODE, LayoutPageKeys.layout_assembly_step_1_page): (start_velocity_mode, dict(controller=controller)),
        (KeyDefs.BTN_START_VELO_MODE, LayoutPageKeys.layout_assembly_step_2_page): (start_velocity_mode, dict(controller=controller)),
        (KeyDefs.BTN_START_VELO_MODE, LayoutPageKeys.layout_assembly_step_3_page): (start_velocity_mode, dict(controller=controller)),

        KeyDefs.COMBO_FAILURE_SELECT: (combo_value_changes, dict()),
        KeyDefs.BTN_SELECT_IMPROVEMENT: (btn_improvement_selection_clicked, dict()),

        KeyDefs.EVENT_CALLBACK_FUNCTION_MAIN_THREAD : ( lambda event, values: invoked_callback_in_main_thread(event, values), dict()),



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
        else:
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