from tkinter import font
import PySimpleGUI as sg
import traceback

from hw_interface.motor_controller import RebelAxisController

from .definitions import font_headline, font_normal, font_small
from .plotting import GraphPlotter

from data_management.model import Improvement, ImprovementInstance
from data_management import data_controller


import enum

class Key(enum.Enum):
    CANVAS = "-CANVAS-"
    FINISHED_REPEATING_MEASUREMENT = "-FINISHED_REPEATING_MEASUREMENT-"


def cancel_improvement_button_clicked(window, ontroller:RebelAxisController,imp_instance):
    data_controller.delete_improvement_instance(imp_instance)
    window.write_event_value("Exit", "No")


def repeat_measurement(window:sg.Window, controller:RebelAxisController, imp_instance:ImprovementInstance, ):
    ...

    print("Repeating!", window, imp_instance, controller)

    stop_func = lambda: window.write_event_value(Key.FINISHED_REPEATING_MEASUREMENT, "Data")
    controller.start_movement_velocity_mode(velocity=10, duration=3, invoke_stop_function = stop_func)


def measurement_finished(event, values, window, imp_instance, controller):
    print("measurement finished")




def improvement_window(controller:RebelAxisController, imp_instance:ImprovementInstance):
    title, description = imp_instance.improvement.title, imp_instance.improvement.description
    description = """This is a very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very  long text"""

    c1 = sg.Col([
        [sg.T(title, font=font_headline)], 
        [sg.Multiline(description, font=font_normal, no_scrollbar=True, write_only=True, expand_x=True, expand_y=True)],
        
        ], expand_x=True, expand_y=True, vertical_alignment="top",background_color="orange")
    
    c2 = sg.Col([
        [sg.Image("gui/assembly_pictures/step_1_resize.png", size=(300,300))]
        ], vertical_alignment="top", background_color="green")

    c3 = sg.Col([
        [sg.Canvas(key=Key.CANVAS, size=(200,200))],
    ], expand_x=True, expand_y=True, background_color="purple", element_justification="center")


    bottom_button_bar = sg.Col([
        [sg.B("Messung starten", size=(20,2), k=repeat_measurement), sg.B("Abbrechen", k=cancel_improvement_button_clicked, size=(20,2)), ]
    ], vertical_alignment="bottom", justification="center", element_justification="center", background_color="blue", expand_x=True, )

    layout = [
        [c1, c2],
        [c3],
        [bottom_button_bar],
        
        ]
    
    window = sg.Window("Fehler beheben", layout, modal=True, size=(1000,600),location=(0,0) , finalize=True)

    plotter = GraphPlotter(window[Key.CANVAS])
    # plotter.plot_data([],[])

    
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        elif callable(event):
            event(window, controller, imp_instance)
        else:
            try:
                func = key_function_map.get(event)
                func(event, values, window, imp_instance, controller)
            except:
                print("ERROR: Event = ", event)
                print(traceback.format_exc())
        
        
        
    window.close()


key_function_map = {
    Key.FINISHED_REPEATING_MEASUREMENT: measurement_finished

}


if __name__ == "__main__":
    imp = data_controller.get_random_improvement_instance()

    controller = RebelAxisController()

    # print("imp = ", imp, "controller = ", controller)

    # improvement_window(controller, "Test")

