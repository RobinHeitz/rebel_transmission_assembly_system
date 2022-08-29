import PySimpleGUI as sg
import traceback

from data_management.model import Improvement, ImprovementInstance
from data_management import data_controller


import enum

class Key(enum.Enum):
    CANCEL_IMPROVEMENT = "-CANCEL_IMPROVEMENT-"




def cancel_improvement_button_clicked(event, values, window:sg.Window,imp_id):
    ...
    data_controller.delete_improvement_instance(imp_id)
    window.write_event_value("Exit", "No")
    


def improvement_window(imp_id):
    ...
    layout = [
        [sg.Text(f"{imp_id} / ID = {imp_id}")],
        [sg.B("Abbrechen", k=Key.CANCEL_IMPROVEMENT), ]
        ]
    
    
    window = sg.Window("Fehler beheben", layout, modal=True, size=(1000,600))
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        
        try:
            func = key_function_map.get(event)
            func(event, values, window, imp_id)
        except:
            print("ERROR: Event = ", event)
            print(traceback.format_exc())
        
        
        
    window.close()


key_function_map = {
    Key.CANCEL_IMPROVEMENT: cancel_improvement_button_clicked,
}


if __name__ == "__main__":
    improvement_window()

