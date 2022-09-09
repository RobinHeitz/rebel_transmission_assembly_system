import PySimpleGUI as sg
import traceback

from gui.add_improvement.pages import layout
from gui.add_improvement.definitions import AddImprovementKeys as Keys

from data_management.model import AssemblyStep, FailureType, Improvement, Failure
from data_management import data_controller

from logs.setup_logger import setup_logger
from start_app import combo_value_changes
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

@function_prints
def assembly_step_changed(event, values):
    input_values_changed(event, values)
    step = values[event]
    with data_controller.session_context() as session:
        improvements = session.query(Improvement).filter_by(assembly_step = step).all()
        window[Keys.LISTBOX_IMPROVEMENTS].update(values = improvements)


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
        
        if len(input_values[Keys.LISTBOX_IMPROVEMENTS]) == 0:
            return False

    except KeyError:
        return False
    return True    


@function_prints
def btn_cancel_window(*args):
    ...
    window.close()



@function_prints
def btn_save_improvement(event, values):
    ...
    with data_controller.session_context() as session:
        description = input_values[Keys.MULTI_LINE_DESCRIPTION]
        assembly_step = input_values[Keys.COMBO_ASSEMBLY_STEP]
        failure_type = FailureType.not_measurable.name
        
        f = Failure(description = description, assembly_step = assembly_step, failure_type = failure_type)
        session.add(f)
        f.improvements = input_values[Keys.LISTBOX_FAILURES]
        session.commit()
    window.close()






#####################
### MAIN FUNCTION ###
#####################


KEY_FUNCTION_MAP = {
    Keys.BTN_SAVE_IMPROVEMENT: btn_save_improvement, 
    Keys.BTN_CANCEL_ADD_IMPROVEMENT: btn_cancel_window,

    Keys.COMBO_ASSEMBLY_STEP: assembly_step_changed,
    Keys.MULTI_LINE_DESCRIPTION: input_values_changed,
    Keys.LISTBOX_FAILURES: input_values_changed,

}

window:sg.Window = None
input_values = {}



def add_improvement_window():
    global window
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
    add_improvement_window()