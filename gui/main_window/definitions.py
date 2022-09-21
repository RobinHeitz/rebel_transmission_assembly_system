from data_management.model import TransmissionConfiguration
import enum
import PySimpleGUI as sg

from gui.gui_helpers import Colors

##################
# Style definitions
###################

class LayoutTypes(enum.Enum):
    config = 1
    assembly = 2


class KeyDefs(enum.Enum):
    """Represents all needed Keys as Enum-Class."""

    LAYOUT_CONFIG = "-LAYOUT_CONFIG-"
    LAYOUT_ASSEMBLY = "-LAYOUT_ASSEMBLY-"

    BTN_NAV_PREVIOUS_PAGE = "-BTN_NAV_PREVIOUS_PAGE-"
    BTN_NAV_NEXT_PAGE = "-BTN_NAV_NEXT_PAGE-"

    COL_TRANSMISSION_CONFIG = "-COL_TRANSMISSION_CONFIG-"
    RADIO_BUTTON_80_CLICKED = "-RADIO_BUTTON_80_CLICKED-"
    RADIO_BUTTON_105_CLICKED = "-RADIO_BUTTON_105_CLICKED-"
    BTN_CONNECT_CAN = "-BTN_CONNECT_CAN-"

    BTN_READ_ERROR_CODES = "-BTN_READ_ERROR_CODES-"

    COL_SOFTWAR_UPDATE = "-COL_SOFTWAR_UPDATE-"
    BTN_SOFTWARE_UPDATE = "-BTN_SOFTWARE_UPDATE-"
    SOFTWARE_UPDATE_FEEDBACK = "-SOFTWARE_UPDATE_FEEDBACK-"
    PROGRESSBAR_SOFTWARE_UPDATE = "-PROGRESSBAR_SOFTWARE_UPDATE-"

    TEXT_CAN_CONNECTED_STATUS = "-TEXT_CAN_CONNECTED_STATUS-"

    CHECKBOX_HAS_ENCODER = "-CHECKBOX_HAS_ENCODER-"
    CHECKBOX_HAS_BRAKE = "-CHECKBOX_HAS_BRAKE-"

    BTN_CHECK_MOVEABILITY = "-BTN_CHECK_MOVEABILITY-"

    BTN_START_VELO_MODE = "-BTN_START_VELO_MODE-"
    
    COL_FAILURE_SELECTION_CONTAINER = "-COL_FAILURE_SELECTION_CONTAINER-"
    FRAME_FAILURE_DETECTION = "-FRAME_FAILURE_DETECTION-"
    COMBO_FAILURE_SELECT = "-COMBO_FAILURE_SELECT-"

    EVENT_CALLBACK_FUNCTION_MAIN_THREAD = "-EVENT_CALLBACK_FUNCTION_MAIN_THREAD-"
    IMAGE_ASSEMBLY = "-IMAGE_ASSEMBLY-"
    MULTILINE_ASSEMBLY_INSTRUCTION = "-MULTILINE_ASSEMBLY_INSTRUCTION-"


    LISTBOX_POSSIBLE_IMPROVEMENTS = "-LISTBOX_POSSIBLE_IMPROVEMENTS-"
    BTN_SELECT_IMPROVEMENT = "-BTN_SELECT_IMPROVEMENT-"

    TEXT_HIGH_CURRENT_FAILURE_DETECTED = "-TEXT_HIGH_CURRENT_FAILURE_DETECTED-"

    CANVAS_GRAPH_PLOTTING = "-CANVAS_GRAPH_PLOTTING-"
    TEXT_MIN_MAX_CURRENT_VALUES = "-TEXT_MIN_MAX_CURRENT_VALUES-"

    BTN_REJECT_TRANSMISSION_NO_IMPROVEMENT = "-BTN_REJECT_TRANSMISSION_NO_IMPROVEMENT-"

    BTN_ADD_FAILURE = "-BTN_ADD_FAILURE-"
    BTN_ADD_IMPROVEMENT = "-BTN_ADD_IMPROVEMENT-"



class ElementVisibilityStates(enum.Enum):

    state_not_connected = -10
    state_connected = -9
    state_configured = -8
    

    # config_state_1_cannot_go_next = -1
    config_state_can_go_next = 2

    assembly_state_1_can_start_measure = 3
    assembly_state_2_is_doing_measure =  4
    
    assembly_state_3_measure_finished_no_failure_detected =  5
    assembly_state_4_measure_finished_user_detects_additional_error = 6
    assembly_state_5_measure_finished_failure_automatically_detected = 7

    improvement_success = 8
    improvement_no_success = 9
    no_more_improvements_reject_transmission = 10




_btn_add_failure_improvement_visible = {
    KeyDefs.BTN_ADD_FAILURE: {"visible": True, "disabled": False},
    KeyDefs.BTN_ADD_IMPROVEMENT: {"visible": True, "disabled": False},
}

_btn_add_failure_improvement_invisible = {
    KeyDefs.BTN_ADD_FAILURE: {"visible": False, "disabled": True},
    KeyDefs.BTN_ADD_IMPROVEMENT: {"visible": False, "disabled": True},
}


_nav_disabled =  {
    KeyDefs.BTN_NAV_NEXT_PAGE:{"disabled": True, "button_color":sg.theme_button_color()},
    KeyDefs.BTN_NAV_PREVIOUS_PAGE:{"disabled": True, "visible":False}, 
}

_nav_enabled =  {
    KeyDefs.BTN_NAV_NEXT_PAGE:{"disabled": False, "button_color":("black", sg.YELLOWS[0])},
    KeyDefs.BTN_NAV_PREVIOUS_PAGE:{"disabled": True, "visible":False}, 
}

_failure_frames_invisible = {
    KeyDefs.FRAME_FAILURE_DETECTION: {"visible":False},
    KeyDefs.TEXT_HIGH_CURRENT_FAILURE_DETECTED: {"visible":False},
    KeyDefs.COL_FAILURE_SELECTION_CONTAINER: {"visible":False},
    KeyDefs.LISTBOX_POSSIBLE_IMPROVEMENTS: {"visible":False},
    
}



ELEMENT_VISIBILITY_MAP = {
    ElementVisibilityStates.state_not_connected : {
        KeyDefs.COL_TRANSMISSION_CONFIG: {"visible": False},
        KeyDefs.COL_SOFTWAR_UPDATE: {"visible": False},
        # KeyDefs.TEXT_CAN_CONNECTED_STATUS: {"text": "Der PEAK CAN-Adapter ist nicht angeschlossen.", "text_color" : Colors.red},
        **_nav_disabled,
        **_btn_add_failure_improvement_visible,
    },

    
    ElementVisibilityStates.state_connected : {
        KeyDefs.COL_TRANSMISSION_CONFIG: {"visible": True},
        KeyDefs.TEXT_CAN_CONNECTED_STATUS: {"text_color": Colors.green},
        KeyDefs.BTN_CONNECT_CAN: {"disabled": True},
        KeyDefs.COL_SOFTWAR_UPDATE: {"visible": False},
        **_nav_disabled,
        **_btn_add_failure_improvement_visible,
    },
    
    ElementVisibilityStates.state_configured : {
        KeyDefs.COL_SOFTWAR_UPDATE: {"visible": True},
        **_nav_disabled,
        **_btn_add_failure_improvement_visible,
    },
    

    ElementVisibilityStates.config_state_can_go_next: {
        KeyDefs.PROGRESSBAR_SOFTWARE_UPDATE: {"bar_color": (Colors.green, None)},
        **_nav_enabled,
        **_btn_add_failure_improvement_visible,

    },
    
    ElementVisibilityStates.assembly_state_1_can_start_measure: {
        **_nav_disabled, 
        KeyDefs.BTN_START_VELO_MODE: {"visible": True, "disabled": False},
        KeyDefs.CANVAS_GRAPH_PLOTTING: {"visible": False},

        **_failure_frames_invisible,
        KeyDefs.TEXT_MIN_MAX_CURRENT_VALUES: {"visible":False},
        **_btn_add_failure_improvement_visible,
    },
    
    ElementVisibilityStates.assembly_state_2_is_doing_measure: {
        **_nav_disabled,
        KeyDefs.BTN_START_VELO_MODE: {"disabled": True, "visible":False},
        KeyDefs.CANVAS_GRAPH_PLOTTING: {"visible": True},
        **_failure_frames_invisible,
        KeyDefs.TEXT_MIN_MAX_CURRENT_VALUES: {"visible":False},
        **_btn_add_failure_improvement_invisible,

    },
   
   
    ElementVisibilityStates.assembly_state_3_measure_finished_no_failure_detected: {
        **_nav_enabled,

        KeyDefs.BTN_START_VELO_MODE: {"disabled": True, "visible":False},
        KeyDefs.CANVAS_GRAPH_PLOTTING: {"visible": True},

        **_failure_frames_invisible,
        KeyDefs.TEXT_MIN_MAX_CURRENT_VALUES: {"visible":True},
        **_btn_add_failure_improvement_visible,
    },
    
   
    ElementVisibilityStates.assembly_state_4_measure_finished_user_detects_additional_error: {
        **_nav_disabled, 
        
        KeyDefs.BTN_START_VELO_MODE: {"disabled": True, "visible":False},
        KeyDefs.CANVAS_GRAPH_PLOTTING: {"visible": True},

        KeyDefs.FRAME_FAILURE_DETECTION: {"visible":True},
        KeyDefs.COL_FAILURE_SELECTION_CONTAINER: {"visible":True},
        KeyDefs.LISTBOX_POSSIBLE_IMPROVEMENTS: {"visible": True},


        KeyDefs.TEXT_HIGH_CURRENT_FAILURE_DETECTED: {"visible":False},
        KeyDefs.TEXT_MIN_MAX_CURRENT_VALUES: {"visible":True},
        **_btn_add_failure_improvement_visible,
    },
    
    ElementVisibilityStates.assembly_state_5_measure_finished_failure_automatically_detected: {
        **_nav_disabled, 
        
        KeyDefs.BTN_START_VELO_MODE: {"disabled": True, "visible":False},
        KeyDefs.CANVAS_GRAPH_PLOTTING: {"visible": True},

        KeyDefs.FRAME_FAILURE_DETECTION: {"visible":True},
        KeyDefs.COL_FAILURE_SELECTION_CONTAINER: {"visible":False},
        KeyDefs.LISTBOX_POSSIBLE_IMPROVEMENTS: {"visible": True},
        KeyDefs.TEXT_HIGH_CURRENT_FAILURE_DETECTED: {"visible":True},
        KeyDefs.TEXT_MIN_MAX_CURRENT_VALUES: {"visible":True},
        **_btn_add_failure_improvement_visible,
    },
    
    ElementVisibilityStates.improvement_success: {
        **_nav_enabled, 
        KeyDefs.FRAME_FAILURE_DETECTION: {"visible": False},
        **_btn_add_failure_improvement_visible,
    },

    ElementVisibilityStates.improvement_no_success: {
        **_nav_disabled, 
        KeyDefs.COMBO_FAILURE_SELECT: {"visible": False},
        KeyDefs.COL_FAILURE_SELECTION_CONTAINER: {"visible":False},
        **_btn_add_failure_improvement_visible,
    },
    
    ElementVisibilityStates.no_more_improvements_reject_transmission: {
        KeyDefs.BTN_NAV_NEXT_PAGE: {"visible": False},
        KeyDefs.BTN_NAV_PREVIOUS_PAGE: {"visible": False},

        KeyDefs.FRAME_FAILURE_DETECTION: {"visible": False},
        KeyDefs.BTN_REJECT_TRANSMISSION_NO_IMPROVEMENT: {"visible": True, "disabled":False},
        **_btn_add_failure_improvement_visible,
    },
}


def get_element_update_values(state: ElementVisibilityStates, is_last_page = False):
    if state not in ELEMENT_VISIBILITY_MAP: raise NotImplementedError(f"State is not implemented: {state}")
    conf = ELEMENT_VISIBILITY_MAP[state]
    if is_last_page:
        updates = {"button_color": sg.GREENS[3], "text":"Fertig"}
        current_btn_conf = conf[KeyDefs.BTN_NAV_NEXT_PAGE]
        conf[KeyDefs.BTN_NAV_NEXT_PAGE] = {**current_btn_conf, **updates}
    return conf
    



##################
# CLASS DEFINITION
##################

class TransmissionSize(enum.Enum):
    size_80 = "80"
    size_105 = "105"


class TransmissionConfigHelper:
    size = TransmissionSize.size_80
    has_encoder = False, 
    has_brake = False

    def __str__(self):
        return f"Transmission configuration: Size = {self.size.value} / has encoder = {self.has_encoder} / has brake = {self.has_brake}"

    def set_size(self, size:TransmissionSize):
        self.size = size
    
    def set_encoder_flag(self, has_encoder:bool):
        self.has_encoder = has_encoder
    
    def set_brake_flag(self, has_brake:bool):
        self.has_brake = has_brake

    def get_transmission_config(self):

        # import pdb
        # pdb.set_trace()

        if self.size == TransmissionSize.size_80:
            if self.has_encoder == True:
                config = TransmissionConfiguration.config_80_encoder
            else:
                config = TransmissionConfiguration.config_80
        elif self.size == TransmissionSize.size_105:
            if self.has_encoder == True and self.has_brake == True:
                config = TransmissionConfiguration.config_105_break_encoder
            elif self.has_encoder == True:
                config = TransmissionConfiguration.config_105_encoder
            elif self.has_brake == True:
                config = TransmissionConfiguration.config_105_break
            else:
                config = TransmissionConfiguration.config_105
        
        else: 
            raise Exception("Transmission Size error: Size must be of type TransmissionSize (Enum).")
        
        return config




