import PySimpleGUI as sg

from .definitions import font_headline, font_normal, font_small, get_color_arg

from .definitions import ImprovementWindowKeys as Key

from .definitions import get_image


def generate_improvement_window_layout(title, description, start, cancel ):



    c_desc = sg.Col([
            [sg.T(title, font=font_headline)], 
            [sg.Multiline(description, font=font_normal, no_scrollbar=True, write_only=True, expand_x=True, expand_y=True)],
            [sg.Col(layout=[[sg.B("Behebungsmaßnahme starten", k=Key.BTN_START_IMPROVEMENT_METHOD)]], justification="center")]
            
            ], expand_x=True, expand_y=True, vertical_alignment="top",background_color=get_color_arg())
        
    c_image = sg.Col([
        [get_image("gui/assembly_pictures/step1.png", size=(300,300))],
        ], vertical_alignment="top", background_color=get_color_arg())

    c_canvas = sg.Col([
        [sg.Canvas(key=Key.CANVAS, size=(50,50))],
        [sg.T("", k="-result-")],
    ], expand_x=True, expand_y=True, background_color=get_color_arg(), visible=False, k=Key.COL_CANVAS)

    c_image_assembly_steps = sg.Col([
        [
            get_image("gui/assembly_pictures/cable_not_connected.png", size=(350,350), k=Key.IMG_IMPROVEMENT),
        ],
        [sg.B("Weiter", k=Key.BTN_SHOW_NEXT_IMAGE)],

    ], visible=False, k=Key.COL_IMAGE_DESCRIPTION, justification="center")



    bottom_button_bar = sg.Col([
        [
            sg.B("Messung starten", size=(20,2), k=start), 
            sg.B("Abbrechen", k=cancel, size=(20,2)),
            sg.B("Fehler behoben", size=(20,2), button_color="green", k=Key.BTN_FAILURE_FIXED, visible=False),
            sg.B("Fehler besteht weiterhin", size=(20,2), button_color="red", k=Key.BTN_FAILURE_STILL_EXISTS, visible=False),
            sg.B("Schließen", size=(20,2), button_color="red", k=Key.BTN_CLOSE_IMPROVEMENT_WINDOW, visible=False),
            
            ]
    ], vertical_alignment="bottom", justification="center", element_justification="center", background_color=get_color_arg(), expand_x=True, )

    layout = [
        [c_desc,],
        [sg.pin(c_image_assembly_steps, shrink=True)],
        [c_canvas],
        [bottom_button_bar],
        
    ]
    return layout