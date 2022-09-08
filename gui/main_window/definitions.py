from data_management.model import TransmissionConfiguration
import enum

##################
# Style definitions
###################
font_headline = "Helvetiva 25"
font_normal = "Helvetica 15"
font_small = "Helvetica 13"

class LayoutTypes(enum.Enum):
    config = 1
    assembly = 2



class KeyDefs(enum.Enum):
    """Represents all needed Keys as Enum-Class."""

    LAYOUT_CONFIG = "-LAYOUT_CONFIG-"
    LAYOUT_ASSEMBLY = "-LAYOUT_ASSEMBLY-"

    BTN_NAV_PREVIOUS_PAGE = "-BTN_NAV_PREVIOUS_PAGE-"
    BTN_NAV_NEXT_PAGE = "-BTN_NAV_NEXT_PAGE-"

    RADIO_BUTTON_80_CLICKED = "-RADIO_BUTTON_80_CLICKED-"
    RADIO_BUTTON_105_CLICKED = "-RADIO_BUTTON_105_CLICKED-"
    BTN_CONNECT_CAN = "-BTN_CONNECT_CAN-"

    BTN_READ_ERROR_CODES = "-BTN_READ_ERROR_CODES-"

    BTN_SOFTWARE_UPDATE = "-BTN_SOFTWARE_UPDATE-"
    SOFTWARE_UPDATE_FEEDBACK = "-SOFTWARE_UPDATE_FEEDBACK-"
    SOFTWARE_UPDATE_DONE = "-SOFTWARE_UPDATE_DONE-"
    PROGRESSBAR_SOFTWARE_UPDATE = "-PROGRESSBAR_SOFTWARE_UPDATE-"
    TEXT_SOFTWARE_UPDATE_STATUS_TEXT = "-TEXT_SOFTWARE_UPDATE_STATUS_TEXT-"

    TEXT_CAN_CONNECTED_STATUS = "-TEXT_CAN_CONNECTED_STATUS-"

    CHECKBOX_HAS_ENCODER = "-CHECKBOX_HAS_ENCODER-"
    CHECKBOX_HAS_BRAKE = "-CHECKBOX_HAS_BRAKE-"

    BTN_CHECK_MOVEABILITY = "-BTN_CHECK_MOVEABILITY-"

    BTN_START_VELO_MODE = "-BTN_START_VELO_MODE-"
    
    COL_FAILURE_SELECTION_CONTAINER = "-COL_FAILURE_SELECTION_CONTAINER-"
    FRAME_FAILURE_DETECTION = "-FRAME_FAILURE_DETECTION-"
    COMBO_FAILURE_SELECT = "-COMBO_FAILURE_SELECT-"

    # EVENT_INITIAL_MEASUREMENT_FINISHED = "-EVENT_INITIAL_MEASUREMENT_FINISHED-"
    EVENT_CALLBACK_FUNCTION_MAIN_THREAD = "-EVENT_CALLBACK_FUNCTION_MAIN_THREAD-"

    IMAGE_ASSEMBLY = "-IMAGE_ASSEMBLY-"
    
    
    
    # LISTBOX_POSSIBLE_FAILURES = "-LISTBOX_POSSIBLE_FAILURES-"

    LISTBOX_POSSIBLE_IMPROVEMENTS = "-LISTBOX_POSSIBLE_IMPROVEMENTS-"
    BTN_SELECT_IMPROVEMENT = "-BTN_SELECT_IMPROVEMENT-"

    TEXT_HIGH_CURRENT_FAILURE_DETECTED = "-TEXT_HIGH_CURRENT_FAILURE_DETECTED-"


    # Event key from threading (updates, finished etc.)

    # Element keys (text, etc.)
    CANVAS_GRAPH_PLOTTING = "-CANVAS_GRAPH_PLOTTING-"
    TEXT_MIN_MAX_CURRENT_VALUES = "-TEXT_MIN_MAX_CURRENT_VALUES-"



class ElementVisibilityStates(enum.Enum):
    config_state_1_cannot_go_next = 1
    config_state_2_can_go_next = 2

    assembly_state_1_can_start_measure = 3
    assembly_state_2_is_doing_measure =  4
    
    assembly_state_3_measure_finished_no_failure_detected =  5
    assembly_state_4_measure_finished_user_detects_additional_error = 6
    assembly_state_5_measure_finished_failure_automatically_detected = 7

    improvement_was_success = 8
    improvement_was_no_success = 9



_nav_disabled =  {
    KeyDefs.BTN_NAV_NEXT_PAGE:{"disabled": True},
    KeyDefs.BTN_NAV_PREVIOUS_PAGE:{"disabled": True, "visible":False}, 
}

_nav_enabled =  {
    KeyDefs.BTN_NAV_NEXT_PAGE:{"disabled": False},
    KeyDefs.BTN_NAV_PREVIOUS_PAGE:{"disabled": True, "visible":False}, 
}

_failure_frames_invisible = {
    KeyDefs.FRAME_FAILURE_DETECTION: {"visible":False},
    KeyDefs.TEXT_HIGH_CURRENT_FAILURE_DETECTED: {"visible":False},
    KeyDefs.COL_FAILURE_SELECTION_CONTAINER: {"visible":False},
    KeyDefs.LISTBOX_POSSIBLE_IMPROVEMENTS: {"visible":False},
    
}



ELEMENT_VISIBILITY_MAP = {
    ElementVisibilityStates.config_state_1_cannot_go_next : {
        **_nav_disabled,
    },

    ElementVisibilityStates.config_state_2_can_go_next: {
        **_nav_enabled,
    },
    
    ElementVisibilityStates.assembly_state_1_can_start_measure: {
        **_nav_disabled, 
        KeyDefs.BTN_START_VELO_MODE: {"disabled": False},
        KeyDefs.CANVAS_GRAPH_PLOTTING: {"visible": True},

        **_failure_frames_invisible,
        KeyDefs.TEXT_MIN_MAX_CURRENT_VALUES: {"visible":False},
    },
    
    ElementVisibilityStates.assembly_state_2_is_doing_measure: {
        **_nav_disabled,
        KeyDefs.BTN_START_VELO_MODE: {"disabled": True, "visible":False},
        KeyDefs.CANVAS_GRAPH_PLOTTING: {"visible": True},
        **_failure_frames_invisible,
        KeyDefs.TEXT_MIN_MAX_CURRENT_VALUES: {"visible":False},
    },
   
   
    ElementVisibilityStates.assembly_state_3_measure_finished_no_failure_detected: {
        **_nav_enabled,

        KeyDefs.BTN_START_VELO_MODE: {"disabled": True, "visible":False},
        KeyDefs.CANVAS_GRAPH_PLOTTING: {"visible": True},

        **_failure_frames_invisible,
        KeyDefs.TEXT_MIN_MAX_CURRENT_VALUES: {"visible":True},
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
    },
    
    ElementVisibilityStates.improvement_was_success: {
        **_nav_enabled, 
        KeyDefs.FRAME_FAILURE_DETECTION: {"visible": False},
    },

    ElementVisibilityStates.improvement_was_no_success: {
        **_nav_disabled, 
        KeyDefs.COMBO_FAILURE_SELECT: {"visible": False},
    },
    


}




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




