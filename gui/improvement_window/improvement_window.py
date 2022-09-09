import PySimpleGUI as sg
import traceback

from hw_interface.definitions import ExceptionPcanNoCanIdFound
from hw_interface.motor_controller import RebelAxisController

from data_management.model import AssemblyStep, FailureType, Improvement, ImprovementInstance, Failure, FailureInstance, Measurement, Transmission
from data_management import data_controller

from .definitions import font_headline, font_normal, font_small, ImprovementWindowKeys as Key, ElementVisibilityState, ELEMENT_VISIBILITY_MAP

from .pages import generate_improvement_window_layout

from ..plotting import GraphPlotter

from gui.main_window.start_measurement import start_measurement

from current_limits import get_current_limit_for_assembly_step

import image_resize


from logs.setup_logger import setup_logger
logger = setup_logger("improvemet_window")

sg.theme("DarkTeal10")

###################
### DEFINITIONS ###
###################



window = None
controller = None
plotter = None

fail_instance = None
improvement = None
imp_instance = None
assembly_step = None

current_image_index = 1

#################
### FUNCTIONS ###
#################

def function_prints(f):
    def wrap(*args, **kwargs):
        ...
        logger.info(f"--- {f.__name__}() called")
        return f(*args, **kwargs)
    return wrap




@function_prints
def set_element_state(new_state:ElementVisibilityState):
    logger.info(f"new State = {new_state}")
    if new_state not in ELEMENT_VISIBILITY_MAP:
        raise Exception("ERROR: State is not part of ELEMENT_VISIBILITy_MAP")
    
    config = ELEMENT_VISIBILITY_MAP.get(new_state)
    
    for el in config.keys():
        window[el].update(**config[el])




###################
### BUTTON CLICKED:
###################

@function_prints
def btn_close_improvement_window(*args):
    ...

@function_prints
def close_window():
    window.write_event_value("Exit", None)

@function_prints
def btn_cancel_improvement(*args):
    ...
    

@function_prints
def btn_start_improvement(*args):
    """Invoked by button click, calls motor_controller's disconnect-method."""
    
    cable_disconnect = improvement.cable_must_disconnected
    if cable_disconnect:
        global current_image_index
        current_image_index = 1
        controller.disconnect()
        set_element_state(ElementVisibilityState.doing_improvement_steps)
    else:
        img_update(improvement.image_filename)
        set_element_state(ElementVisibilityState.doing_last_improvement_step)


@function_prints
def btn_show_next_image(*args):
    global current_image_index

    current_image_index += 1
    if current_image_index == 2:
        img_update(improvement.image_filename)

    elif current_image_index == 3:
        img_update("cable_connected.png")
        set_element_state(ElementVisibilityState.doing_last_improvement_step)
    


@function_prints
def img_update(img_name):
    path = f"gui/assembly_pictures/{img_name}"
    s = (350,350)
    img = image_resize.resize_bin_output(path, size=s)
    window[Key.IMG_IMPROVEMENT].update(img, size=s)
    


@function_prints
def improvement_process_steps_done(*args):
    ...
    try:
        controller.connect()
    except ExceptionPcanNoCanIdFound as e:
        import traceback
        logger.warning("Received exception: CAN-ID could not be found.")
        logger.warning(traceback.format_exc())
    
    set_element_state(ElementVisibilityState.improvement_steps_done)





###############################
### START REPEATING MEASUREMENT
###############################
@function_prints
def btn_start_measurement(imp_instance:ImprovementInstance, *args):
    # logger.info(args)
    set_element_state(ElementVisibilityState.doing_measurement)
    start_measurement(controller, assembly_step, measurement_finished, measurement_aborted_due_to_error, plotter)


@function_prints
def measurement_finished(m:Measurement):
    def _update_text(passed:bool):
        if passed:
            window[Key.TEXT_MEASUREMENT_RESULT].update(f"Messung erfolgreich! Max. current: {m.max_current}", text_color=sg.GREENS[3])
        else:
            window[Key.TEXT_MEASUREMENT_RESULT].update(f"Messung nicht erfolgreich: Max. current is {m.max_current}", text_color="red")
    
    data_controller.update_improvement_measurement_relation(m, imp_instance)    
    passed = is_measurement_ok(m)
    _update_text(passed)

    if fail_instance.failure.failure_type == FailureType.overcurrent:
        set_element_state(ElementVisibilityState.finished_measurement)
        
        if passed == True:
            data_controller.set_success_status(imp_instance, True)
            window[Key.BTN_CLOSE_IMPROVEMENT_WINDOW].update(visible=True, button_color=sg.GREENS[3])
        else:
            data_controller.set_success_status(imp_instance, False)
            window[Key.BTN_CLOSE_IMPROVEMENT_WINDOW].update(visible=True, button_color="red")
    
    else:
        logger.info(f"Failure is not measurable; Therefore personal feedback necessary")
        set_element_state(ElementVisibilityState.measurement_user_detects_additional_errors)
       

@function_prints
def measurement_aborted_due_to_error(error_code, *args, **kwargs):
    ...
    logger.info(error_code)


@function_prints
def is_measurement_ok(m:Measurement):
    logger.debug(f"evaluate_measurable_failures()")
    limit = get_current_limit_for_assembly_step(assembly_step)
    if m.max_current > limit:
        return False
    return True


##############################
### Handle improvement process
##############################



@function_prints
def cancel_improvement_button_clicked(imp_instance):
    logger.debug(f"cancel_improvement_button_clicked()")
    data_controller.delete_improvement_instance(imp_instance)
    data_controller.data_controller.delete_failure_instance(fail_instance)
    # window.write_event_value("Exit", None)
    close_window()




@function_prints
def user_selected_failure_is_fixed():
    """Btn click: For not-measureable failures, user decides whether failure is fixed or not."""
    logger.debug(f"user_selected_failure_is_fixed")
    data_controller.set_success_status(imp_instance, True)
    close_window()


@function_prints
def user_selected_failure_still_exists():
    """Btn click: For not-measureable failures, user decides whether failure is fixed or not."""
    logger.debug(f"user_selected_failure_still_exists")
    data_controller.set_success_status(imp_instance, False)
    close_window()

    


###################################################################################################################
###################################################################################################################
###################################################################################################################

@function_prints
def improvement_window(c:RebelAxisController, t:Transmission, selected_failure:Failure, selected_improvement: Improvement, invalid_measurement:Measurement, step:AssemblyStep):
    global controller, fail_instance, imp_instance, window, plotter, assembly_step, improvement
    
    controller = c
    assembly_step = step
    improvement = selected_improvement
    fail_instance, imp_instance = data_controller.setup_improvement_start(t, selected_failure, selected_improvement, invalid_measurement, assembly_step)
    title, description = imp_instance.improvement.title, imp_instance.improvement.description
    
    # layout = generate_improvement_window_layout(title, description, start_repeat_measurement, cancel_improvement_button_clicked)
    layout = generate_improvement_window_layout(title, description)

    window = sg.Window(f"Fehler beheben: {selected_failure}", layout, modal=True, size=(1000,600),location=(0,0) , finalize=True, resizable=True, no_titlebar=True)
    plotter = GraphPlotter(window[Key.CANVAS])
    plotter.plot_data([],[])

    set_element_state(ElementVisibilityState.starting_default_screen)

    window.maximize()
    
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        elif callable(event):
            event(imp_instance)
        else:
            try:
                func = key_function_map.get(event)
                func(event, values, imp_instance)
            except:
                logger.error(f"Error while executing function from key-function-dict: Event={event}")
                logger.error(traceback.format_exc())
        
        
        
    window.close()

    return fail_instance, imp_instance


key_function_map = {
    Key.BTN_START_IMPROVEMENT_METHOD: lambda *args: btn_start_improvement(),
    Key.BTN_NEXT_IMPROVEMENT_STEP: btn_show_next_image,
    # Key.BTN_FINISHED_IMPROVEMENT_STEPS: lambda *args: set_element_state(ElementVisibilityState.improvement_steps_done),
    Key.BTN_FINISHED_IMPROVEMENT_STEPS: improvement_process_steps_done,


    Key.BTN_CANCEL_IMPROVEMENT: btn_cancel_improvement, 
    Key.BTN_START_MEASUREMENT: btn_start_measurement,

    Key.BTN_CLOSE_IMPROVEMENT_WINDOW: lambda *args: btn_close_improvement_window(),
    Key.BTN_FAILURE_STILL_EXISTS: lambda *args: user_selected_failure_still_exists(),
    Key.BTN_FAILURE_FIXED: lambda *args: user_selected_failure_is_fixed(),

    Key.FINISHED_MEASUREMENT: measurement_finished,
}

