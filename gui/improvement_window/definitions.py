from data_management.model import TransmissionConfiguration
import enum
import random

import image_resize
import PySimpleGUI as sg
##################
# Style definitions
###################
font_headline = "Helvetiva 25"
font_normal = "Helvetica 15"
font_small = "Helvetica 13"

COLS_WITH_COLOR = False

def get_image(path, size, **kwargs):
    data = image_resize.resize_bin_output(path, size)
    return sg.Image(data, size=size, **kwargs)

def get_color_arg():
    if COLS_WITH_COLOR == True:
        colors = ["red", "blue", "green", "purple", "orange", "brown", "yellow"]
        return random.choice(colors)
    else:
        return None


class ImprovementWindowKeys(enum.Enum):
    CANVAS = "-CANVAS-"
    COL_CANVAS = "-COL_CANVAS-"
    TEXT_MEASUREMENT_RESULT = "-TEXT_MEASUREMENT_RESULT-"

    BTN_START_MEASUREMENT = "-BTN_START_MEASUREMENT-"
    BTN_CANCEL_IMPROVEMENT = "-BTN_CANCEL_IMPROVEMENT-"

    FINISHED_MEASUREMENT = "-FINISHED_REPEATING_MEASUREMENT-"
    
    BTN_FAILURE_FIXED = "-BTN_FAILURE_FIXED-"
    BTN_FAILURE_STILL_EXISTS = "-BTN_FAILURE_STILL_EXISTS-"
    BTN_CLOSE_IMPROVEMENT_WINDOW = "-BTN_CLOSE_IMPROVEMENT_WINDOW-"

    BTN_START_IMPROVEMENT_METHOD = "-BTN_START_IMPROVEMENT_METHOD-"
    COL_IMAGE_DESCRIPTION = "-COL_IMAGE_DESCRIPTION-"
    
    IMG_IMPROVEMENT = "-IMG_IMPROVEMENT-"
    BTN_NEXT_IMPROVEMENT_STEP = "-BTN_NEXT_IMPROVEMENT_STEP-"



class ElementVisibilityState(enum.Enum):
    step_1_default_screen = 1
    step_2_improvement_steps_done = 2
    step_3_doing_measure = 3
    
    step_4_finished_measure = 4
    step_5_finished_measure_user_detects_additional_errors = 5

    


_nav_disabled =  {
    None:{"disabled": True},
}




ELEMENT_VISIBILITY_MAP = {
    ElementVisibilityState.step_1_default_screen : {
        ImprovementWindowKeys.COL_CANVAS: {"visible":False},
        ImprovementWindowKeys.BTN_START_MEASUREMENT: {"visible":False},
    },

    ElementVisibilityState.step_2_improvement_steps_done : {
        ImprovementWindowKeys.BTN_START_MEASUREMENT: {"visible":True},
        ImprovementWindowKeys.COL_CANVAS: {"visible":True},
        ImprovementWindowKeys.COL_IMAGE_DESCRIPTION: {"visible":False},
        ImprovementWindowKeys.TEXT_MEASUREMENT_RESULT: {"visible": False},
    },
    
    ElementVisibilityState.step_3_doing_measure : {
        ImprovementWindowKeys.BTN_START_MEASUREMENT: {"visible":False},
        ImprovementWindowKeys.BTN_CANCEL_IMPROVEMENT: {"visible": False},
    },
    
    ElementVisibilityState.step_4_finished_measure : {
        ImprovementWindowKeys.BTN_CANCEL_IMPROVEMENT: {"visible": False},
        ImprovementWindowKeys.TEXT_MEASUREMENT_RESULT: {"visible": True},
        ImprovementWindowKeys.BTN_CLOSE_IMPROVEMENT_WINDOW: {"visible": True},
    },
    
    ElementVisibilityState.step_5_finished_measure_user_detects_additional_errors : {
        ImprovementWindowKeys.BTN_CANCEL_IMPROVEMENT: {"visible": False},
        ImprovementWindowKeys.TEXT_MEASUREMENT_RESULT: {"visible": True},
        ImprovementWindowKeys.BTN_CLOSE_IMPROVEMENT_WINDOW: {"visible": False},
        ImprovementWindowKeys.BTN_FAILURE_FIXED: {"visible": True},
        ImprovementWindowKeys.BTN_FAILURE_STILL_EXISTS: {"visible": True},

    },
    
}