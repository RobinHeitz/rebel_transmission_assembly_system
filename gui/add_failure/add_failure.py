import PySimpleGUI as sg
import traceback

from gui.add_failure.pages import layout
from gui.add_failure.definitions import AddFailureKeys as Keys

from data_management.model import AssemblyStep

from logs.setup_logger import setup_logger
logger = setup_logger("start_app")



def function_prints(f):
    def wrap(*args, **kwargs):
        ...
        logger.info(f"--- {f.__name__}() called")
        return f(*args, **kwargs)
    return wrap

# @function_prints
# def set_element_state(new_state:ElementVisibilityStates):
#     config = get_element_update_values(new_state, is_last_page=is_last_assembly_step)
#     for el in config.keys():
#         settings = config.get(el)
#         window[el].update(**settings)



#################
### FUNCTIONS ###
#################

# @function_prints
def input_values_changed(event, values):
    global input_values
    input_values[event] = values[event]
    valid_values = validate_values()
    window[Keys.BTN_SAVE_FAILURE].update(disabled=(not valid_values))


def validate_values():
    try:
        if input_values[Keys.COMBO_ASSEMBLY_STEP] == None:
            return False
        if len(input_values[Keys.MULTI_LINE_DESCRIPTION]) == 0:
            return False
    
    except KeyError:
        return False
    return True    


@function_prints
def btn_cancel_window(*args):
    ...
    window.close()



@function_prints
def btn_save_failure(*args):
    ...




#####################
### MAIN FUNCTION ###
#####################


KEY_FUNCTION_MAP = {
    Keys.BTN_SAVE_FAILURE: btn_save_failure, 
    Keys.BTN_CANCEL_ADD_FAILURE: btn_cancel_window,

    Keys.COMBO_ASSEMBLY_STEP: input_values_changed,
    Keys.MULTI_LINE_DESCRIPTION: input_values_changed,

}

window:sg.Window = None
input_values = {}



def add_failure_window():
    global window
    ...

    window = sg.Window(f"Fehler hinzufügen", layout, modal=True, size=(500,600), finalize=True, resizable=False, no_titlebar=True)
    # sg.main_get_debug_data()
    
    while True:
        try:
            event, values = window.read()
        except KeyboardInterrupt:
            break
        
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        elif callable(event):
            ...
        else:
            try:
                func = KEY_FUNCTION_MAP.get(event)
                func(event, values)
            except:
                logger.error(f"Error while executing function from key-function-dict: Event={event}")
                logger.error(traceback.format_exc())

    window.close()

if __name__ == "__main__":
    add_failure_window()