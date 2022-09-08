import PySimpleGUI as sg
import traceback
from hw_interface.definitions import ExceptionPcanNoCanIdFound

from hw_interface.motor_controller import RebelAxisController

from .definitions import font_headline, font_normal, font_small, ImprovementWindowKeys as Key
from .pages import generate_improvement_window_layout

from ..plotting import GraphPlotter


from data_management.model import AssemblyStep, FailureType, Improvement, ImprovementInstance, Failure, FailureInstance, Measurement, Transmission
from data_management import data_controller


from gui.main_window.start_measurement import start_measurement
# from gui.main_window import start_measurement
# from gui.main_window import pages


from current_limits import get_current_limit_for_assembly_step

import image_resize

import enum
import random

sg.theme("DarkTeal10")



from logs.setup_logger import setup_logger
logger = setup_logger("improvemet_window")


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
def close_window():
    window.write_event_value("Exit", None)


####################################
### (Mechanical) IMPROVEMENT PROCESS
####################################
@function_prints
def start_improvement(*args):
    """Invoked by button click, calls motor_controller's disconnect-method."""
    window[Key.BTN_START_IMPROVEMENT_METHOD].update(visible=False)
    window[Key.COL_IMAGE_DESCRIPTION].update(visible=True)
    controller.disconnect()
    


@function_prints
def show_next_image(*args):
    global current_image_index
    
    def img_update(img_name):
        path = f"gui/assembly_pictures/{img_name}"
        s = (300,300)
        img = image_resize.resize_bin_output(path, size=s)
        window[Key.IMG_IMPROVEMENT].update(img, size=s)
    

    if current_image_index == 1:
        img_update(improvement.image_filename)

    elif current_image_index == 2:
        img_update("cable_connected.png")
    elif current_image_index == 3:
        col = window[Key.COL_IMAGE_DESCRIPTION]

        window[Key.COL_IMAGE_DESCRIPTION].update(visible=False)
        return improvement_process_finished()
    current_image_index += 1



@function_prints
def improvement_process_finished():
    ...
    try:
        controller.connect()
    except ExceptionPcanNoCanIdFound as e:
        import traceback
        logger.warning("Received exception: CAN-ID could not be found.")
        logger.warning(traceback.format_exc())





###############################
### START REPEATING MEASUREMENT
###############################
@function_prints
def start_repeat_measurement(imp_instance:ImprovementInstance, ):
    logger.debug(f"start_repeat_measurement() | imp_instance: {imp_instance}")
    window[Key.COL_CANVAS].update(visible=True)
    start_measurement(controller, AssemblyStep.step_1_no_flexring, measurement_finished, measurement_aborted_due_to_error, plotter)

@function_prints
def measurement_finished(m:Measurement):
    logger.debug(f"measurement_finished() | measurement: {m} | failure={fail_instance.failure}")
    data_controller.update_improvement_measurement_relation(m, imp_instance)    
    
    if fail_instance.failure.failure_type == FailureType.overcurrent:
        passed = is_measurement_ok(m)
        if passed == True:
            window["-result-"].update("green")
            data_controller.set_success_status(imp_instance, True)
        else:
            window["-result-"].update("red")
            data_controller.set_success_status(imp_instance, False)
        
        window[Key.BTN_CLOSE_IMPROVEMENT_WINDOW].update(visible=True)
    
    else:
        logger.info(f"Failure is not measurable; Therefore personal feedback necessary")
        window[Key.BTN_FAILURE_FIXED].update(visible=True)
        window[Key.BTN_FAILURE_STILL_EXISTS].update(visible=True)

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
    
    layout = generate_improvement_window_layout(title, description, start_repeat_measurement, cancel_improvement_button_clicked)

    window = sg.Window(f"Fehler beheben: {selected_failure}", layout, modal=True, size=(1000,600),location=(0,0) , finalize=True, resizable=True, no_titlebar=True)
    plotter = GraphPlotter(window[Key.CANVAS])
    plotter.plot_data([],[])

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
    Key.FINISHED_REPEATING_MEASUREMENT: measurement_finished,
    Key.BTN_FAILURE_STILL_EXISTS: lambda *args: user_selected_failure_still_exists(),
    Key.BTN_FAILURE_FIXED: lambda *args: user_selected_failure_is_fixed(),
    Key.BTN_CLOSE_IMPROVEMENT_WINDOW: lambda *args: close_window(),
    Key.BTN_START_IMPROVEMENT_METHOD: lambda *args: start_improvement(),
    Key.BTN_SHOW_NEXT_IMAGE: show_next_image,

}

