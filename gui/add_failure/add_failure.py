import PySimpleGUI as sg
import traceback

from .pages import layout
from .definitions import AddFailureKeys as Keys




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




#####################
### MAIN FUNCTION ###
#####################


KEY_FUNCTION_MAP = {

}



def add_failure_window():
    ...

    window = sg.Window(f"Fehler hinzufügen", layout, modal=True, size=(500,600), finalize=True, resizable=False, no_titlebar=True)

    while True:
        event, values = window.read()
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