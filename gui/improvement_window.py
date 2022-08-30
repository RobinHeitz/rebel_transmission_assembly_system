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


def cancel_improvement_button_clicked(window, imp_instance):
    data_controller.delete_improvement_instance(imp_instance)
    window.write_event_value("Exit", "No")


def repeat_measurement(window:sg.Window, imp_instance:ImprovementInstance):
    ...

    print("Repeating!", window, imp_instance)




def improvement_window(imp_instance:ImprovementInstance):
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
        [sg.Canvas(key=Key.CANVAS, size=(1,1))],
    ], expand_x=True, expand_y=True, background_color="purple")


    bottom_button_bar = sg.Col([
        [sg.B("Messung starten", size=(20,2), k=repeat_measurement), sg.B("Abbrechen", k=cancel_improvement_button_clicked, size=(20,2)), ]
    ], vertical_alignment="bottom", justification="center", element_justification="center", background_color="blue", expand_x=True, )

    layout = [
        [c1, c2],
        [c3],
        [bottom_button_bar],
        
        ]
    
    window = sg.Window("Fehler beheben", layout, modal=True, size=(1000,600),location=(0,0) , finalize=False)

    # plotter = GraphPlotter(window[Key.CANVAS])
    # plotter.plot_data([],[])

    
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        elif callable(event):
            event(window, imp_instance)
        else:
            try:
                func = key_function_map.get(event)
                func(event, values, window, imp_instance)
            except:
                print("ERROR: Event = ", event)
                print(traceback.format_exc())
        
        
        
    window.close()


key_function_map = {

}


if __name__ == "__main__":
    improvement_window()

