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
    BTN_FINISHED_IMPROVEMENT_STEPS = "-BTN_FINISHED_IMPROVEMENT_STEPS-"



class ElementVisibilityState(enum.Enum):
    starting_default_screen = 1
    doing_improvement_steps = 2
    doing_last_improvement_step = 3


    improvement_steps_done = 4
    doing_measurement = 5
    
    finished_measurement = 6
    measurement_user_detects_additional_errors = 7

    



ELEMENT_VISIBILITY_MAP = {
    ElementVisibilityState.starting_default_screen : {
        ImprovementWindowKeys.COL_CANVAS: {"visible":False},
        ImprovementWindowKeys.BTN_START_MEASUREMENT: {"visible":False},
    },

   
    ElementVisibilityState.doing_improvement_steps : {
        ImprovementWindowKeys.COL_CANVAS: {"visible":False},
        ImprovementWindowKeys.BTN_START_MEASUREMENT: {"visible":False},
        ImprovementWindowKeys.BTN_START_IMPROVEMENT_METHOD: {"visible":False},
        ImprovementWindowKeys.COL_IMAGE_DESCRIPTION: {"visible":True},
        ImprovementWindowKeys.BTN_NEXT_IMPROVEMENT_STEP: {"visible": True},
        ImprovementWindowKeys.BTN_FINISHED_IMPROVEMENT_STEPS: {"visible": False},
    },
   
    ElementVisibilityState.doing_last_improvement_step : {
        ImprovementWindowKeys.COL_CANVAS: {"visible":False},
        ImprovementWindowKeys.BTN_START_MEASUREMENT: {"visible":False},
        ImprovementWindowKeys.BTN_START_IMPROVEMENT_METHOD: {"visible":False},
        ImprovementWindowKeys.COL_IMAGE_DESCRIPTION: {"visible":True},
        ImprovementWindowKeys.BTN_NEXT_IMPROVEMENT_STEP: {"visible": False},
        ImprovementWindowKeys.BTN_FINISHED_IMPROVEMENT_STEPS: {"visible": True},
    },

    ElementVisibilityState.improvement_steps_done : {
        ImprovementWindowKeys.BTN_START_MEASUREMENT: {"visible":True},
        ImprovementWindowKeys.COL_CANVAS: {"visible":True},
        ImprovementWindowKeys.COL_IMAGE_DESCRIPTION: {"visible":False},
        ImprovementWindowKeys.TEXT_MEASUREMENT_RESULT: {"visible": False},
        ImprovementWindowKeys.BTN_NEXT_IMPROVEMENT_STEP: {"visible": False},
        ImprovementWindowKeys.BTN_FINISHED_IMPROVEMENT_STEPS: {"visible": True},
    },
    
    ElementVisibilityState.doing_measurement : {
        ImprovementWindowKeys.BTN_START_MEASUREMENT: {"visible":False},
        ImprovementWindowKeys.BTN_CANCEL_IMPROVEMENT: {"visible": False},
    },
    
    ElementVisibilityState.finished_measurement : {
        ImprovementWindowKeys.BTN_CANCEL_IMPROVEMENT: {"visible": False},
        ImprovementWindowKeys.TEXT_MEASUREMENT_RESULT: {"visible": True},
        ImprovementWindowKeys.BTN_CLOSE_IMPROVEMENT_WINDOW: {"visible": True},
    },
    
    ElementVisibilityState.measurement_user_detects_additional_errors : {
        ImprovementWindowKeys.BTN_CANCEL_IMPROVEMENT: {"visible": False},
        ImprovementWindowKeys.TEXT_MEASUREMENT_RESULT: {"visible": True},
        ImprovementWindowKeys.BTN_CLOSE_IMPROVEMENT_WINDOW: {"visible": False},
        ImprovementWindowKeys.BTN_FAILURE_FIXED: {"visible": True},
        ImprovementWindowKeys.BTN_FAILURE_STILL_EXISTS: {"visible": True},

    },
    
}