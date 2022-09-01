from fileinput import close
from tkinter import font
import PySimpleGUI as sg
import traceback

from hw_interface.motor_controller import RebelAxisController

from .definitions import font_headline, font_normal, font_small
from .plotting import GraphPlotter

from data_management.model import AssemblyStep, FailureType, Improvement, ImprovementInstance, Failure, FailureInstance, Measurement
from data_management import data_controller

from gui import start_measurement
import enum
import random

from logs.setup_logger import setup_logger
logger = setup_logger("improvemet_window")

###################
### DEFINITIONS ###
###################


class Key(enum.Enum):
    CANVAS = "-CANVAS-"
    FINISHED_REPEATING_MEASUREMENT = "-FINISHED_REPEATING_MEASUREMENT-"
    BTN_FAILURE_FIXED = "-BTN_FAILURE_FIXED-"
    BTN_FAILURE_STILL_EXISTS = "-BTN_FAILURE_STILL_EXISTS-"
    BTN_CLOSE_IMPROVEMENT_WINDOW = "-BTN_CLOSE_IMPROVEMENT_WINDOW-"


window = None
controller = None
plotter = None

fail_instance = None
imp_instance = None

COLS_WITH_COLOR = False



#################
### FUNCTIONS ###
#################

def get_color_arg():
    if COLS_WITH_COLOR == True:
        colors = ["red", "blue", "green", "purple", "orange", "brown", "yellow"]
        return random.choice(colors)
    else:
        return None

def close_window():
    window.write_event_value("Exit", None)


def cancel_improvement_button_clicked(imp_instance):
    logger.debug(f"cancel_improvement_button_clicked()")
    data_controller.delete_improvement_instance(imp_instance)
    data_controller.data_controller.delete_failure_instance(fail_instance)
    # window.write_event_value("Exit", None)
    close_window()

def start_repeat_measurement(imp_instance:ImprovementInstance, ):
    logger.debug(f"start_repeat_measurement() | imp_instance: {imp_instance}")
    start_measurement.start_measurement(controller, AssemblyStep.step_1_no_flexring, measurement_finished, plotter)


def measurement_finished(m:Measurement):
    logger.debug(f"measurement_finished() | measurement: {m} | failure={fail_instance.failure}")
    data_controller.append_measurement_to_improvment_instance(m, imp_instance)
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


def is_measurement_ok(m:Measurement):
    # TODO: Check against YAML-Config-File
    logger.debug(f"evaluate_measurable_failures()")
    if m.max_current > 400:
        return False
    return True

def user_selected_failure_is_fixed():
    logger.debug(f"user_selected_failure_is_fixed")
    data_controller.set_success_status(imp_instance, True)
    close_window()


def user_selected_failure_still_exists():
    logger.debug(f"user_selected_failure_still_exists")
    data_controller.set_success_status(imp_instance, False)
    close_window()
    
    



def improvement_window(c:RebelAxisController, selected_failure:Failure, selected_improvement: Improvement, invalid_measurement:Measurement):
    logger.debug(f"""improvement_window() | selected failure: {selected_failure} / 
    selected improvement: {selected_improvement} / (invalid) measurement: {invalid_measurement}""")

    global controller, fail_instance, imp_instance, window, plotter
    controller = c
    fail_instance, imp_instance = data_controller.setup_improvement_start(selected_failure, selected_improvement, invalid_measurement)
    title, description = imp_instance.improvement.title, imp_instance.improvement.description

    c1 = sg.Col([
        [sg.T(title, font=font_headline)], 
        [sg.Multiline(description, font=font_normal, no_scrollbar=True, write_only=True, expand_x=True, expand_y=True)],
        
        ], expand_x=True, expand_y=True, vertical_alignment="top",background_color=get_color_arg())
    
    c2 = sg.Col([
        [sg.Image("gui/assembly_pictures/step_1_resize.png", size=(300,300))]
        ], vertical_alignment="top", background_color=get_color_arg())

    c3 = sg.Col([
        [sg.Canvas(key=Key.CANVAS, size=(50,50))],
        [sg.T("", k="-result-")],
    ], expand_x=True, expand_y=True, background_color=get_color_arg())


    bottom_button_bar = sg.Col([
        [
            sg.B("Messung starten", size=(20,2), k=start_repeat_measurement), 
            sg.B("Abbrechen", k=cancel_improvement_button_clicked, size=(20,2)),
            sg.B("Fehler behoben", size=(20,2), button_color="green", k=Key.BTN_FAILURE_FIXED, visible=False),
            sg.B("Fehler besteht weiterhin", size=(20,2), button_color="red", k=Key.BTN_FAILURE_STILL_EXISTS, visible=False),
            sg.B("Schließen", size=(20,2), button_color="red", k=Key.BTN_CLOSE_IMPROVEMENT_WINDOW, visible=False),
            
            ]
    ], vertical_alignment="bottom", justification="center", element_justification="center", background_color=get_color_arg(), expand_x=True, )

    layout = [
        [c1, c2],
        [c3],
        [bottom_button_bar],
        
        ]

    window = sg.Window(f"Fehler beheben: {selected_failure}", layout, modal=True, size=(1000,600),location=(0,0) , finalize=True, resizable=True)
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


key_function_map = {
    Key.FINISHED_REPEATING_MEASUREMENT: measurement_finished,
    Key.BTN_FAILURE_STILL_EXISTS: lambda *args: user_selected_failure_still_exists(),
    Key.BTN_FAILURE_FIXED: lambda *args: user_selected_failure_is_fixed(),
    Key.BTN_CLOSE_IMPROVEMENT_WINDOW: lambda *args: close_window(),

}

