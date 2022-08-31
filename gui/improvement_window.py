from tkinter import font
import PySimpleGUI as sg
import traceback

from hw_interface.motor_controller import RebelAxisController

from .definitions import font_headline, font_normal, font_small
from .plotting import GraphPlotter

from data_management.model import AssemblyStep, Improvement, ImprovementInstance, Failure, FailureInstance, Measurement
from data_management import data_controller

from gui import start_measurement
import enum

###################
### DEFINITIONS ###
###################


class Key(enum.Enum):
    CANVAS = "-CANVAS-"
    FINISHED_REPEATING_MEASUREMENT = "-FINISHED_REPEATING_MEASUREMENT-"


window = None
controller = None
plotter = None

fail_instance = None
imp_instance = None



#################
### FUNCTIONS ###
#################

def cancel_improvement_button_clicked(imp_instance):
    data_controller.delete_improvement_instance(imp_instance)
    window.write_event_value("Exit", "No")


def start_repeat_measurement(imp_instance:ImprovementInstance, ):
    print("Repeating Measurement")
    start_measurement.start_measurement(controller, AssemblyStep.step_1_no_flexring, measurement_finished, plotter)


def measurement_finished(m:Measurement):
    print("measurement finished: M = ", m)



def improvement_window(c:RebelAxisController, selected_failure:Failure, selected_improvement: Improvement, invalid_measurement:Measurement):
    print("***"*5)
    print("improve_window() starting ||| controler = ", c, "| selected failure:", selected_failure, " | selected_improvement = ", selected_improvement)

    global controller, fail_instance, imp_instance, window, plotter
    controller = c
    fail_instance, imp_instance = data_controller.setup_improvement_start(selected_failure, selected_improvement)
    title, description = imp_instance.improvement.title, imp_instance.improvement.description

    c1 = sg.Col([
        [sg.T(title, font=font_headline)], 
        [sg.Multiline(description, font=font_normal, no_scrollbar=True, write_only=True, expand_x=True, expand_y=True)],
        
        ], expand_x=True, expand_y=True, vertical_alignment="top",background_color="orange")
    
    c2 = sg.Col([
        [sg.Image("gui/assembly_pictures/step_1_resize.png", size=(300,300))]
        ], vertical_alignment="top", background_color="green")

    c3 = sg.Col([
        [sg.Canvas(key=Key.CANVAS, size=(50,50))],
    ], expand_x=True, expand_y=True, background_color="purple", element_justification="center")


    bottom_button_bar = sg.Col([
        [sg.B("Messung starten", size=(20,2), k=start_repeat_measurement), sg.B("Abbrechen", k=cancel_improvement_button_clicked, size=(20,2)), ]
    ], vertical_alignment="bottom", justification="center", element_justification="center", background_color="blue", expand_x=True, )

    layout = [
        [c1, c2],
        [c3],
        [bottom_button_bar],
        
        ]

    window = sg.Window("Fehler beheben", layout, modal=True, size=(1000,600),location=(0,0) , finalize=True, resizable=True)
    plotter = GraphPlotter(window[Key.CANVAS])
    plotter.plot_data([],[])

    
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
                print("ERROR: Event = ", event)
                print(traceback.format_exc())
        
        
        
    window.close()


key_function_map = {
    Key.FINISHED_REPEATING_MEASUREMENT: measurement_finished

}

