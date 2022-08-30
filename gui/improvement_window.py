import PySimpleGUI as sg
import traceback

from data_management.model import Improvement, ImprovementInstance
from data_management import data_controller


import enum

class Key(enum.Enum):
    CANCEL_IMPROVEMENT = "-CANCEL_IMPROVEMENT-"




# def cancel_improvement_button_clicked(event, values, window:sg.Window,imp_id):
def cancel_improvement_button_clicked(window, imp_instance):
    ...
    data_controller.delete_improvement_instance(imp_instance)
    window.write_event_value("Exit", "No")
    
def my_func(*args):
    print("Function call without args")
    print(args)


def improvement_window(imp_instance:ImprovementInstance):

    layout = [
        
        [sg.Col(layout=[
            [sg.T(imp_instance.improvement.description)]

        ]), sg.Image("gui/assembly_pictures/step_1_resize.png", size=(200,200))],
        
        
        
        [sg.B("Abbrechen", k=lambda: cancel_improvement_button_clicked(window, imp_instance)), sg.B("TEST", k=my_func)],
        
        
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
    Key.CANCEL_IMPROVEMENT: cancel_improvement_button_clicked,
}


if __name__ == "__main__":
    improvement_window()

