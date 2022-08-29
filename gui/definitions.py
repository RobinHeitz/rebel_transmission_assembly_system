from data_management.model import TransmissionConfiguration
import enum


##################
# Style definitions
###################
font_headline = "Helvetiva 25"
font_normal = "Helvetica 15"
font_small = "Helvetica 13"


class KeyDefs(enum.Enum):
    """Represents all needed Keys as Enum-Class."""

    BTN_NAV_PREVIOUS_PAGE = "-BTN_NAV_PREVIOUS_PAGE-"
    BTN_NAV_NEXT_PAGE = "-BTN_NAV_NEXT_PAGE-"

    RADIO_BUTTON_80_CLICKED = "-RADIO_BUTTON_80_CLICKED-"
    RADIO_BUTTON_105_CLICKED = "-RADIO_BUTTON_105_CLICKED-"
    BTN_CONNECT_CAN = "-BTN_CONNECT_CAN-"
    BTN_SOFTWARE_UPDATE = "-BTN_SOFTWARE_UPDATE-"

    CHECKBOX_HAS_ENCODER = "-CHECKBOX_HAS_ENCODER-"
    CHECKBOX_HAS_BRAKE = "-CHECKBOX_HAS_BRAKE-"

    BTN_CHECK_MOVEABILITY = "-BTN_CHECK_MOVEABILITY-"

    BTN_START_VELO_MODE = "-BTN_START_VELO_MODE-"
    BTN_STOP_VELO_MODE = "-BTN_STOP_VELO_MODE-"

    # BTN_INDICATOR_DETECTION = "-BTN_INDICATOR_DETECTION-"
    # FRAME_INDICATOR = "-FRAME_INDICATOR-"
    # COMBO_INDICATOR_SELECT = "-COMBO_INDICATOR_SELECT"

    BTN_FAILURE_DETECTION = "-BTN_FAILURE_DETECTION-"
    FRAME_FAILURE_DETECTION = "-FRAME_FAILURE_DETECTION-"
    COMBO_FAILURE_SELECT = "-COMBO_FAILURE_SELECT-"
    
    
    
    LISTBOX_POSSIBLE_FAILURES = "-LISTBOX_POSSIBLE_FAILURES-"
    FRAME_POSSIBLE_FAILURES = "-FRAME_POSSIBLE_FAILURES-"
    BTN_SELECT_FAILURE = "-BTN_SELECT_FAILURE-"

    FRAME_POSSIBLE_IMPROVEMENTS = "-FRAME_POSSIBLE_IMPROVEMENTS-"
    LISTBOX_POSSIBLE_IMPROVEMENTS = "-LISTBOX_POSSIBLE_IMPROVEMENTS-"
    BTN_SELECT_IMPROVEMENT = "-BTN_SELECT_IMPROVEMENT-"

    # BTN_FAILURE_DETECTION = "-BTN_FAILURE_DETECTION-"
    # FRAME_FAILURE = "-FRAME_FAILURE-"
    # COMBO_FAILURE_SELECT = "-COMBO_FAILURE_SELECT"




    # Event key from threading (updates, finished etc.)
    SOFTWARE_UPDATE_FEEDBACK = "-SOFTWARE_UPDATE_FEEDBACK-"
    SOFTWARE_UPDATE_DONE = "-SOFTWARE_UPDATE_DONE-"
    UPDATE_GRAPH = "-UPDATE_GRAPH-"
    FINISHED_VELO_STOP_GRAPH_UPDATING = "-FINISHED_VELO_STOP_GRAPH_UPDATING-"


    # Element keys (text, etc.)
    TEXT_CAN_CONNECTED_STATUS = "-TEXT_CAN_CONNECTED_STATUS-"
    PROGRESSBAR_SOFTWARE_UPDATE = "-PROGRESSBAR_SOFTWARE_UPDATE-"
    TEXT_SOFTWARE_UPDATE_STATUS_TEXT = "-TEXT_SOFTWARE_UPDATE_STATUS_TEXT-"
    CANVAS_GRAPH_PLOTTING = "-CANVAS_GRAPH_PLOTTING-"
    TEXT_MIN_MAX_CURRENT_VALUES = "-TEXT_MIN_MAX_CURRENT_VALUES-"




##################
# CLASS DEFINITION
##################

class LayoutPageKeys(enum.Enum):
    layout_config_page = "-LAYOUT_CONFIG_PAGE-"
    layout_assembly_step_1_page = "-LAYOUT_ASSEMBLY_STEP_1_PAGE-"
    layout_assembly_step_2_page = "-LAYOUT_ASSEMBLY_STEP_2_PAGE-"
    layout_assembly_step_3_page = "-LAYOUT_ASSEMBLY_STEP_3_PAGE-"

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




