# %%

import PySimpleGUI as sg


def shaded_overlay(top_window, alpha=0.6, background_color="black"):
    window = sg.Window("", layout=[[]], modal=True, finalize=True,
                       resizable=False, no_titlebar=True, background_color=background_color)
    window.set_alpha(alpha)
    window.maximize()
    window.move_to_center()
    window.refresh()

    top_window()
    window.close()
