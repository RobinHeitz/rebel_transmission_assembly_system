from multiprocessing.sharedctypes import Value
import traceback 
import PySimpleGUI as sg
import time, threading

import traceback

import image_resize

from data_management.model import AssemblyStep, Failure, FailureType, ImprovementInstance, Measurement
from data_management import data_controller, data_transformation

from hw_interface.motor_controller import RebelAxisController
from hw_interface.definitions import ExceptionPcanIllHardware, ExceptionPcanNoCanIdFound
from current_limits import get_current_limit_for_assembly_step

from gui.main_window.definitions import KeyDefs, ElementVisibilityStates, get_element_update_values, LayoutTypes
from gui.main_window.definitions import TransmissionConfigHelper, TransmissionSize
from gui.main_window.pages import get_assembly_instruction, get_headline, main_layout, get_assembly_step_data

from gui.plotting import GraphPlotter
from gui.shaded_overlay import shaded_overlay

from gui.improvement_window import improvement_window
from gui.improvement_window.improvement_window import STATUS_CANCEL, STATUS_CLOSE_FAIL_NOT_FIXED, STATUS_USER_SELECTED_FAILURE_FIXED, STATUS_USER_SELECTED_FAILURE_IS_NOT_FIXED
from gui.add_improvement.add_improvement import add_improvement_window
from gui.add_failure.add_failure import add_failure_window

from gui.main_window import start_measurement

from logs.setup_logger import setup_logger
logger = setup_logger("start_app")

def get_image(path, size, **kwargs):
    data = image_resize.resize_bin_output(path, size)
    return sg.Image(data, size=size, **kwargs)


def function_prints(f):
    def wrap(*args, **kwargs):
        ...
        logger.info(f"--- {f.__name__}() called")
        return f(*args, **kwargs)
    return wrap

@function_prints
def set_element_state(new_state:ElementVisibilityStates):
    logger.info(f"New Element State: {new_state}")
    config = get_element_update_values(new_state, is_last_page=is_last_assembly_step)
    for el in config.keys():
        settings = config.get(el)
        window[el].update(**settings)

@function_prints
def get_condition_for_next_page():
    return condition_functions_dictionary[(active_layout, current_assembly_step)]



################################################
### CLOSING/ ABORTION OF PROGRAMM OR PARTS OF IT
################################################


@function_prints
def btn_reject_transmission_no_improvements_left(*args):
    """When a specific failure selected, there might be no more improvements left. Transmission is regarded as rejected or n.i.o output."""
    close_application()





@function_prints
def close_application():
    controller.stop_movement()
    controller.shut_down()
    window.close()


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
def radio_size_is_clicked(size:TransmissionSize):
    if controller.connected:
        set_element_state(ElementVisibilityStates.config_state_2_can_go_next)
    
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

    try:
        controller.connect()
    except ExceptionPcanIllHardware as e:
        logger.error(e)
        logger.error(traceback.format_exc())
    except ExceptionPcanNoCanIdFound as e:
        logger.error(e)
        logger.error(traceback.format_exc())
    
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



######################
### CHECK ERROR CODES:
######################

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
def start_velocity_mode(event, values, *args):
    """Invoked by Btn click: Start Measurement"""
    limit = get_current_limit_for_assembly_step(current_assembly_step)
    set_element_state(ElementVisibilityStates.assembly_state_2_is_doing_measure)
    start_measurement.start_measurement(controller, current_assembly_step, measurement_finished_callback,measurement_error_callback ,plotter, limit)


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
    logger.info(f"Error code: {error} / assembly_step = {current_assembly_step}")
    failure = data_controller.get_failure_not_moving_OC(current_assembly_step)
    window[KeyDefs.TEXT_HIGH_CURRENT_FAILURE_DETECTED].update(f"Es wurde ein Fehler erkannt: {failure}", text_color="red", visible=True)
    # window[KeyDefs.COMBO_FAILURE_SELECT].update(values=[failure], value=failure)
    update_combo_failure_values([failure])
    update_listbox_improvement_values(failure)
    set_element_state(ElementVisibilityStates.assembly_state_5_measure_finished_failure_automatically_detected)




@function_prints
def update_combo_failure_values(failures, index=0):
    window[KeyDefs.COMBO_FAILURE_SELECT].update(values=failures, value=failures[index])

@function_prints
def update_listbox_improvement_values(f:Failure, *args, **kwargs):
    """Shows Frame + Listbox with possible Improvements."""
    improvements = data_controller.get_improvements_for_failure(current_assembly_step, f, *args, **kwargs)
    
    if len(improvements) > 0:
        window[KeyDefs.FRAME_FAILURE_DETECTION].update(visible=True)
        window[KeyDefs.LISTBOX_POSSIBLE_IMPROVEMENTS].update(improvements, set_to_index=[0,])

    else:
        set_element_state(ElementVisibilityStates.no_more_improvements_reject_transmission)
        window[KeyDefs.FRAME_FAILURE_DETECTION].update(visible=False)
        sg.popup("Keine weitere Behebungsmaßnahme","Es ist keine weitere Fehlerbehebungsmaßnahme hinterlegt. Wenn du eine weiter findest, füge sie bitte hinzu. Solltest du den Fehler nicht finden können, ist das Getriebe Ausschuss.")



@function_prints
def is_measurement_ok(m:Measurement):
    logger.debug(f"evaluate_measurable_failures()")
    limit = get_current_limit_for_assembly_step(current_assembly_step)
    if m.max_current > limit:
        return False
    return True


@function_prints
def measurement_finished(m:Measurement):
    """Invoked by start_measurement.start_measurement. Callback function for updating gui elements based on finished measurement."""
    logger.error(f"measurement = {m} / id = {m.id}")
    
    def _update_text(passed:bool):
        if passed:
            window[KeyDefs.TEXT_MIN_MAX_CURRENT_VALUES].update(f"Messung erfolgreich! Max. Strom: {m.max_current}", text_color=sg.GREENS[3], visible=True)
        else:
            window[KeyDefs.TEXT_MIN_MAX_CURRENT_VALUES].update(f"Messung nicht erfolgreich! Max. Strom: {m.max_current}", text_color="red", visible=True)
    
    passed = is_measurement_ok(m)
    _update_text(passed)
    predict_failure(m, passed)


@function_prints
def predict_failure(measurement: Measurement, passed:bool):
    """Tries to predict < Indicator > (e.g. Overcurrent) based on currently measurement taken. Gets called after graph updating has stopped. """
    
    if passed == False:
        failure = data_controller.get_failure_overcurrent(current_assembly_step)
        set_element_state(ElementVisibilityStates.assembly_state_5_measure_finished_failure_automatically_detected)
        window[KeyDefs.TEXT_HIGH_CURRENT_FAILURE_DETECTED].update(f"Es wurde ein Fehler erkannt: {failure}", text_color="red")
        update_combo_failure_values([failure])
        # window[KeyDefs.COMBO_FAILURE_SELECT].update(values=[failure], value=failure)
        update_listbox_improvement_values(failure)

    else:
        answer  = sg.popup_yes_no("Kein Fehler erkannt", "Die Messung ist in Ordnung, es wurde kein Fehler erkannt. Ist dir sonst noch ein Fehler aufgefallen?")
        if answer == "Yes":
            set_element_state(ElementVisibilityStates.assembly_state_4_measure_finished_user_detects_additional_error)
            
            failures = data_controller.sorted_failures_by_incidents(current_assembly_step)
            update_combo_failure_values(failures)
            # window[KeyDefs.COMBO_FAILURE_SELECT].update(values=failures, value=failures[0])
            update_listbox_improvement_values(failures[0])
        elif answer == "No" or answer == None:
            set_element_state(ElementVisibilityStates.assembly_state_3_measure_finished_no_failure_detected)
        else:
            raise NotImplementedError("This Button Label is not checked against (yet)!")

@function_prints
def combo_value_changes(event, values):
    """If combo's selected value changes, Possible Improvement Window should hide."""
    update_listbox_improvement_values(values[event])


@function_prints
def btn_improvement_selection_clicked(event, values):
    selected_improvement = values[KeyDefs.LISTBOX_POSSIBLE_IMPROVEMENTS][0]
    selected_failure = values[KeyDefs.COMBO_FAILURE_SELECT]
    latest_measure = data_controller.get_current_measurement_instance()
    logger.info(f"btn_improvement_selection_clicked: {selected_improvement} | selected_failure = {selected_failure} | measurement = {latest_measure}")

    return_status, fail_instance, imp_instance = improvement_window.improvement_window(controller, current_transmission, selected_failure, selected_improvement, latest_measure, current_assembly_step)
    logger.debug(f"Received status from Improvement window: {return_status}")
    
    if return_status == "" or return_status is None:
        raise ValueError("'return_stats' from improvement_window should NEVER be empty string or None.")
    if return_status == STATUS_CANCEL:
        # fail_instance and imp_instance got deleted
        return
        ...
    elif return_status == STATUS_CLOSE_FAIL_NOT_FIXED:
        ...
    elif return_status == STATUS_USER_SELECTED_FAILURE_FIXED:
        ...
    elif return_status == STATUS_USER_SELECTED_FAILURE_IS_NOT_FIXED:
        ...
    else:
        raise ValueError(f"'return_status' should be not different from if/elif's: {return_status}")
    

    imp_instance = data_controller.refresh_improvement_instance(imp_instance.id)

    if imp_instance.successful == True:
        set_element_state(ElementVisibilityStates.improvement_success)
    else:
        set_element_state(ElementVisibilityStates.improvement_no_success)
        update_listbox_improvement_values(selected_failure)

    
######################################################
# FUNCTIONS FOR ENABLING / DISABLING NAVIGATION BUTTONS
######################################################


@function_prints
def _nav_next_page(event, values):
    """Called when user clicks on "Next"-Button. Manages hide/show of layouts etc."""
    global current_assembly_step, active_layout, is_last_assembly_step
    condition = get_condition_for_next_page()
    
    if not callable(condition):
        raise ValueError("Error, condition should be a function and therefore callable")

    if condition():

        if active_layout == LayoutTypes.config:
            active_layout = LayoutTypes.assembly
            window[KeyDefs.LAYOUT_CONFIG].update(visible=False)
            window[KeyDefs.LAYOUT_ASSEMBLY].update(visible=True)

        else:
            current_assembly_step = AssemblyStep.next_step(current_assembly_step)
            is_last_assembly_step = AssemblyStep.is_last_step(current_assembly_step)
            
        _update_headline()
        _update_assembly_steps_data()
        set_element_state(ElementVisibilityStates.assembly_state_1_can_start_measure)
    


@function_prints
def _update_headline():
    """Updates headline and assembly description"""
    new_headline = get_headline(active_layout, current_assembly_step)
    instruction = get_assembly_instruction(active_layout, current_assembly_step)
    window["-headline-"].update(new_headline)
    window[KeyDefs.MULTILINE_ASSEMBLY_INSTRUCTION].update(instruction)

@function_prints
def _update_assembly_steps_data():
    image_path = get_assembly_step_data(active_layout, current_assembly_step)
    data = image_resize.resize_bin_output(image_path, (300,300))
    window[KeyDefs.IMAGE_ASSEMBLY].update(data, size=(300,300))
    plotter.plot_data([],[])

@function_prints
def _nav_previous_page(event, values):
    """Called when user clicks on "Previous"-Button. Manages hide/show of layouts etc."""




##################################################
### BTN Clicks for adding Failure/ Improvement ###
##################################################

@function_prints
def btn_add_failure(*args):
    shaded_overlay(add_failure_window)

@function_prints
def btn_add_improvement(*args):
    shaded_overlay(add_improvement_window)





#################################
### CONDITIONS FOR NAVIGATION ###
#################################

@function_prints
def condition_leave_config_page():
    """Conditional function, is last condition before new page is loaded."""
    err = is_estop_error()
    if err:
        return False
        
    global current_transmission
    config = transmission_config.get_transmission_config()
    current_transmission = data_controller.create_transmission(config)
    return True

@function_prints
def condition_leave_assembly_step_1():
    ...
    return True

@function_prints
def condition_leave_assembly_step_2():
    ...
    return True

@function_prints
def condition_leave_assembly_step_3():
    close_application()
    return False



#################
### MAIN ROUNTINE
#################

if __name__ == "__main__":
    sg.theme("DarkTeal10")
    
    splash_window = sg.Window("igus", [[get_image("gui/assembly_pictures/igus_logo_transparent.png",size=(640,360))]], transparent_color=sg.theme_background_color(), no_titlebar=True, keep_on_top=True, ).read(timeout=2000, close=True)
   
    window = sg.Window("ReBeL Getriebe Montage & Kalibrierung", main_layout, size=(1200,1000), finalize=True, location=(0,0),resizable=True)

    active_layout = LayoutTypes.config
    current_assembly_step = AssemblyStep.step_1_no_flexring
    is_last_assembly_step = False
    set_element_state(ElementVisibilityStates.config_state_1_cannot_go_next)

    controller, thread_velocity, thread_graph_updater, current_transmission = (None, )*4

    database_last_filter = dict(
        failure = None, 
        improvement = None,
    )


    try:
        controller = RebelAxisController(verbose=False)
        controller.connect()

    except ExceptionPcanIllHardware as e:
        logger.warning(e)
        window[KeyDefs.TEXT_CAN_CONNECTED_STATUS].update(str(e))
        window[KeyDefs.BTN_CONNECT_CAN].update("Verbindung herstellen")
    
    except ExceptionPcanNoCanIdFound as e:
        window[KeyDefs.TEXT_CAN_CONNECTED_STATUS].update(str(e))
        window[KeyDefs.BTN_CONNECT_CAN].update("Try Device again")

    
    transmission_config = TransmissionConfigHelper()
    


    plotter = GraphPlotter(window[KeyDefs.CANVAS_GRAPH_PLOTTING])
    plotter.plot_data([],[])

    window.maximize()


    condition_functions_dictionary = {
        (LayoutTypes.config, AssemblyStep.step_1_no_flexring): condition_leave_config_page,
        (LayoutTypes.assembly, AssemblyStep.step_1_no_flexring):condition_leave_assembly_step_1,
        (LayoutTypes.assembly, AssemblyStep.step_2_with_flexring):condition_leave_assembly_step_2,
        (LayoutTypes.assembly, AssemblyStep.step_3_gearoutput_not_screwed):condition_leave_assembly_step_3,

    }


    key_function_map = {
        KeyDefs.BTN_NAV_NEXT_PAGE: _nav_next_page,
        KeyDefs.BTN_NAV_PREVIOUS_PAGE: _nav_previous_page,

        KeyDefs.RADIO_BUTTON_80_CLICKED: lambda *args: radio_size_is_clicked(size=TransmissionSize.size_80),
        KeyDefs.RADIO_BUTTON_105_CLICKED: lambda *args: radio_size_is_clicked(size=TransmissionSize.size_105),

        KeyDefs.BTN_CONNECT_CAN: btn_connect_can,


        KeyDefs.BTN_SOFTWARE_UPDATE: perform_software_update,
        KeyDefs.SOFTWARE_UPDATE_FEEDBACK: lambda event, values: window[KeyDefs.PROGRESSBAR_SOFTWARE_UPDATE].update_bar(values.get(event)),
        KeyDefs.SOFTWARE_UPDATE_DONE : lambda *args: window[KeyDefs.TEXT_SOFTWARE_UPDATE_STATUS_TEXT].update("Software upgedated"),

        KeyDefs.CHECKBOX_HAS_ENCODER: lambda event, values: transmission_config.set_encoder_flag(values[event]),
        KeyDefs.CHECKBOX_HAS_BRAKE: lambda event, values: transmission_config.set_brake_flag(values[event]),
        
        KeyDefs.BTN_START_VELO_MODE: start_velocity_mode,
        

        KeyDefs.COMBO_FAILURE_SELECT: combo_value_changes,
        KeyDefs.BTN_SELECT_IMPROVEMENT: btn_improvement_selection_clicked,

        KeyDefs.EVENT_CALLBACK_FUNCTION_MAIN_THREAD : lambda event, values: invoked_callback_in_main_thread(event, values),

        KeyDefs.BTN_REJECT_TRANSMISSION_NO_IMPROVEMENT : btn_reject_transmission_no_improvements_left,

        KeyDefs.BTN_ADD_FAILURE: btn_add_failure, 
        KeyDefs.BTN_ADD_IMPROVEMENT: btn_add_improvement, 


    }
    # Event loop
    while True:
        try:
            event, values = window.read()
        except KeyboardInterrupt:
            break
    

        if event in (sg.WIN_CLOSED, 'Exit'):
            break
        elif callable(event):
            event()
        else:
            try:
                func = key_function_map.get(event)
                func(event, values)
            
            
            except TypeError as e:
                logger.error(f"WARNING: Missing event in 'key_functin_map': Event = {event} // values = {values.get(event)}")
                logger.error(traceback.format_exc())
            
            except Exception as e:
                logger.error(f"Error has occured while executing event: {event} | function name: {func.__name__}")
                logger.error(traceback.format_exc())
            

    close_application()