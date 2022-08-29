import PySimpleGUI as sg
import traceback

from data_management.model import Improvement, ImprovementInstance
from data_management import data_controller


import enum

class Key(enum.Enum):
    CANCEL_IMPROVEMENT = "-CANCEL_IMPROVEMENT-"




# def cancel_improvement_button_clicked(event, values, window:sg.Window,imp_id):
def cancel_improvement_button_clicked(*args):
    ...
    event, values, window, imp_id = args
    print("###"*5, *args)
    print("cancel_improvement_button_clicked() | Imp_ID = ", imp_id)
    data_controller.delete_improvement_instance(imp_id)
    window.write_event_value("Exit", "No")
    
def my_func(*args):
    print(args)

def improvement_window(imp_id, imp):

    print("WE GOT IMPROVEMENT ISNTANCE: ", imp)

    imp = data_controller.get_improvement_instance(imp_id)

    layout = [
        
        [sg.Col(layout=[
            [sg.T("imp.improvement.description"),sg.T("TWi")]

        ]), sg.Image("gui/assembly_pictures/step_1_resize.png", size=(200,200))],
        
        
        
        [sg.B("Abbrechen", k=Key.CANCEL_IMPROVEMENT), sg.B("TEST", k=lambda: my_func("BTN Pressed"))]
        
        
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

