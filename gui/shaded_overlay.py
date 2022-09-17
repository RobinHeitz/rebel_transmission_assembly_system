# %%

import PySimpleGUI as sg
from typing import Callable



def shaded_overlay(top_window: Callable, alpha:float=0.6, background_color:str="black"):
    window = sg.Window("", layout=[[]], modal=True, finalize=True,
                       resizable=False, no_titlebar=True, background_color=background_color)
    window.set_alpha(alpha)
    window.maximize()
    window.move_to_center()
    window.refresh()

    returnVal = top_window()
    window.close()
    return returnVal