from data_management.model import TransmissionConfiguration
import enum


##################
# Style definitions
###################
font_headline = "Helvetiva 25"
font_normal = "Helvetica 15"
font_small = "Helvetica 13"



#################
# KEY DEFINITIONS
#################

# Button keys
K_BTN_NAV_PREVIOUS_PAGE = "-K_BTN_NAV_PREVIOUS_PAGE-"
K_BTN_NAV_NEXT_PAGE = "-K_BTN_NAV_NEXT_PAGE-"

K_RADIO_BUTTON_80_CLICKED = "-FUNCTION_RADIO_BUTTON_80_CLICKED-"
K_RADIO_BUTTON_105_CLICKED = "-FUNCTION_RADIO_BUTTON_105_CLICKED-"
K_BTN_CONNECT_CAN = "-KEY_BUTTON_CONNECT_CAN-"
K_BTN_SOFTWARE_UPDATE = "-KEY_BUTTON_SOFTWARE_UPDATE-"

K_CHECKBOX_HAS_ENCODER = "-KEY_CHECKBOX_HAS_ENCODER-"
K_CHECKBOX_HAS_BRAKE = "-KEY_CHECKBOX_HAS_BRAKE-"

K_BTN_START_VELO_MODE = "-KEY_BUTTON_START_VELO_MODE-"
K_BTN_STOP_VELO_MODE = "-KEY_BUTTON_STOP_VELO_MODE-"


# Event key from threading (updates, finished etc.)
K_SOFTWARE_UPDATE_FEEDBACK = "-SOFTWARE_UPDATE_FEEDBACK-"
K_SOFTWARE_UPDATE_DONE = "-SOFTWARE_UPDATE_DONE-"
K_UPDATE_GRAPH = "-K_UPDATE_GRAPH-"
K_FINISHED_VELO_STOP_GRAPH_UPDATING = "-KEY_FINISHED_VELO_STOP_GRAPH_UPDATING-"


# Element keys (text, etc.)
K_TEXT_CAN_CONNECTED_STATUS = "-TEXT_CAN_CONNECTION_STATUS-"
K_PROGRESSBAR_SOFTWARE_UPDATE = "-PROGRESSBAR_SOFTWARE_UPDATE-"
K_TEXT_SOFTWARE_UPDATE_STATUS_TEXT = "-TEXT_SOFTWARE_UPDATE_STATUS_TEXT-"
K_CANVAS_GRAPH_PLOTTING = "-CANVAS_GRAPH_PLOTTING-"
K_TEXT_MIN_MAX_CURRENT_VALUES = "-K_TEXT_MIN_MAX_CURRENT_VALUES-"




##################
# CLASS DEFINITION
##################

class TransmissionSize(enum.Enum):
    size_80 = 1
    size_105 = 2


class TransmissionConfigHelper:
    size = TransmissionSize.size_80
    has_encoder = False, 
    has_brake = False

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




