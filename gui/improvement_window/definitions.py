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
    """Keys in improvement window"""
    CANVAS = "-CANVAS-"
    FINISHED_REPEATING_MEASUREMENT = "-FINISHED_REPEATING_MEASUREMENT-"
    BTN_FAILURE_FIXED = "-BTN_FAILURE_FIXED-"
    BTN_FAILURE_STILL_EXISTS = "-BTN_FAILURE_STILL_EXISTS-"
    BTN_CLOSE_IMPROVEMENT_WINDOW = "-BTN_CLOSE_IMPROVEMENT_WINDOW-"

    BTN_START_IMPROVEMENT_METHOD = "-BTN_START_IMPROVEMENT_METHOD-"
    COL_IMAGE_DESCRIPTION = "-COL_IMAGE_DESCRIPTION-"
    
    IMG_IMPROVEMENT = "-IMG_IMPROVEMENT-"
    # IMG_CABLE_DISCONNECT = "-IMG_CABLE_DISCONNECT-"
    # IMG_IMPROVEMENT_PICURE = "-IMG_IMPROVEMENT_PICURE-"
    # IMG_CABLE_RECONNECT = "-IMG_CABLE_RECONNECT-"
    BTN_SHOW_NEXT_IMAGE = "-BTN_SHOW_NEXT_IMAGE-"

    COL_CANVAS = "-COL_CANVAS-"