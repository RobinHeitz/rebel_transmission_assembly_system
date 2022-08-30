from tkinter import font
import PySimpleGUI as sg
import traceback

from .definitions import font_headline, font_normal, font_small

from data_management.model import Improvement, ImprovementInstance
from data_management import data_controller


import enum

class Key(enum.Enum):
    DUNNO = "-CANCEL_IMPROVEMENT-"




# def cancel_improvement_button_clicked(event, values, window:sg.Window,imp_id):
def cancel_improvement_button_clicked(window, imp_instance):
    ...
    data_controller.delete_improvement_instance(imp_instance)
    window.write_event_value("Exit", "No")
    


def improvement_window(imp_instance:ImprovementInstance):
    title, description = imp_instance.improvement.title, imp_instance.improvement.description

    layout = [
        
        [sg.Col(layout=[
            [sg.T(title, font=font_headline)], 
            [sg.T(description, font=font_normal)],

        ], expand_x=True, vertical_alignment="top"), sg.Image("gui/assembly_pictures/step_1_resize.png", size=(300,300))],
        
        
        
        [sg.B("Abbrechen", k=lambda: cancel_improvement_button_clicked(window, imp_instance)), ],
        
        ]
    
    
    window = sg.Window("Fehler beheben", layout, modal=True, size=(1000,600))
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        elif callable(event):
            event()
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

