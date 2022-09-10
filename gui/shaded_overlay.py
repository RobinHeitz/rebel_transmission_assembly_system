# %%

import PySimpleGUI as sg


class ShadedOverlay():
    def __init__(self, top_window, alpha=0.6, background_color="black"):
        window = sg.Window("", layout=[[]], modal=True, finalize=True, resizable=False, no_titlebar=True, background_color=background_color)
        window.set_alpha(alpha)
        window.maximize()

        top_window()
        window.close()
        


def make_shaded_overlay_window(top_window, alpha=0.6, background_color="black"):
  

    return sg.Window('', layout=[[]], finalize=True, modal=True, resizable=False, no_titlebar=True, background_color=background_color, alpha_channel=alpha)



def shaded_overlay(top_window, alpha=0.6, background_color="black"):
    window = sg.Window("", layout=[[]], modal=True, finalize=True, resizable=False, no_titlebar=True, background_color=background_color)
    window.set_alpha(alpha)
    window.maximize()

    top_window()
    window.close()

if __name__ == "__main__":
    # shaded_overlay()

    make_shaded_overlay_window(None)
