import PySimpleGUI as sg
import traceback

from gui.add_improvement.pages import create_layout
from gui.add_improvement.definitions import AddImprovementKeys as Keys

from gui.gui_helpers import ToggleButtonImageData as TI

from data_management.model import AssemblyStep, FailureType, Improvement, Failure
from data_management import data_controller

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

@function_prints
def assembly_step_changed(event, values):
    input_values_changed(event, values)
    step = values[event]
    with data_controller.session_context() as session:
        failures = session.query(Failure).filter_by(assembly_step = step).all()
        window[Keys.LISTBOX_FAILURES].update(values = failures)

@function_prints
def btn_toggle_cable_disconnect(event, values):
    
    toggle_state = window[Keys.BTN_TOGGLE_CABLE_DISCONNECT].metadata
    toggle_state = not toggle_state
    window[Keys.BTN_TOGGLE_CABLE_DISCONNECT].metadata = toggle_state
    window[Keys.BTN_TOGGLE_CABLE_DISCONNECT].update(image_data=TI.toggle_btn_on if window[Keys.BTN_TOGGLE_CABLE_DISCONNECT].metadata else TI.toggle_btn_off)
    global input_values
    input_values[event] = toggle_state



def input_values_changed(event, values):
    global input_values
    input_values[event] = values[event]
    valid_values = validate_values()
    window[Keys.BTN_SAVE_IMPROVEMENT].update(disabled=(not valid_values))


def validate_values():
    try:
        if input_values[Keys.COMBO_ASSEMBLY_STEP] == None:
            return False
        if len(input_values[Keys.MULTI_LINE_DESCRIPTION]) == 0:
            return False
        
        if len(input_values[Keys.LISTBOX_FAILURES]) == 0:
            return False

        if len(input_values[Keys.INPUT_IMPROVEMENT_TITLE]) == 0:
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
        
        attributes = dict(
            title = input_values[Keys.INPUT_IMPROVEMENT_TITLE],
            description = input_values[Keys.MULTI_LINE_DESCRIPTION],
            assembly_step = input_values[Keys.COMBO_ASSEMBLY_STEP],
            image_filename = None,
            cable_must_disconnected = input_values.get(Keys.BTN_TOGGLE_CABLE_DISCONNECT, False)
        )
        
        improvement = Improvement(**attributes)
        session.add(improvement)
        improvement.failures = input_values[Keys.LISTBOX_FAILURES]
        session.commit()
        session.commit()
    window.close()






#####################
### MAIN FUNCTION ###
#####################


KEY_FUNCTION_MAP = {
    Keys.BTN_SAVE_IMPROVEMENT: btn_save_improvement, 
    Keys.BTN_CANCEL_ADD_IMPROVEMENT: btn_cancel_window,
    
    Keys.BTN_TOGGLE_CABLE_DISCONNECT: btn_toggle_cable_disconnect,

    Keys.COMBO_ASSEMBLY_STEP: assembly_step_changed,
    Keys.INPUT_IMPROVEMENT_TITLE: input_values_changed,
    Keys.MULTI_LINE_DESCRIPTION: input_values_changed,
    Keys.LISTBOX_FAILURES: input_values_changed,

}

window:sg.Window = None
input_values = {
}



def add_improvement_window():
    global window
    window = sg.Window(f"Fehler hinzufügen", create_layout(), modal=True, size=(500,600), finalize=True, resizable=False, no_titlebar=True)
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