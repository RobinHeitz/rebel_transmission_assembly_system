import PySimpleGUI as sg

from .definitions import font_headline, font_normal, font_small, get_color_arg

from .definitions import ImprovementWindowKeys as Key, get_image, font_headline, font_small, font_normal


from gui.gui_helpers import BtnColors, create_btn, get_image


def generate_improvement_window_layout(title, description):

    c_desc = sg.Col([
            [sg.T(title, font=font_headline)], 
            [sg.Multiline(description, font=font_normal, no_scrollbar=True, write_only=True, expand_x=True, expand_y=False, size=(None, 5))],
            [sg.P(), create_btn("Maßnahme starten", key=Key.BTN_START_IMPROVEMENT_METHOD), sg.P(),],

            ], expand_x=True, expand_y=False, vertical_alignment="top",background_color=get_color_arg())
        
    c_canvas = sg.Col([
        [sg.Canvas(key=Key.CANVAS, size=(50,50))],
        [create_btn("Messung starten",key=Key.BTN_START_MEASUREMENT),],
        [sg.T("", k=Key.TEXT_MEASUREMENT_RESULT, font=font_headline)],
    ], expand_x=True, expand_y=True, visible=False, k=Key.COL_CANVAS, element_justification="center")

    c_image_assembly_steps = sg.Col([
        [
            get_image("gui/assembly_pictures/cable_not_connected.png", size=(350,350), k=Key.IMG_IMPROVEMENT),
        ],
        [create_btn("Weiter", key=Key.BTN_NEXT_IMPROVEMENT_STEP, disabled=False), create_btn("Maßnahme durchgeführt",key=Key.BTN_FINISHED_IMPROVEMENT_STEPS, visible=False)]

    ], visible=False, k=Key.COL_IMAGE_DESCRIPTION, justification="center", element_justification="center", )



    bottom_button_bar = sg.Col([
        [
            create_btn("Abbrechen",key=Key.BTN_CANCEL_IMPROVEMENT, disabled=False),
            create_btn("Fehler behoben",key=Key.BTN_FAILURE_FIXED, button_color=BtnColors.green),
            create_btn("Fehler nicht behoben",key=Key.BTN_FAILURE_STILL_EXISTS, button_color=BtnColors.red),
            create_btn("Schließen",key=Key.BTN_CLOSE_IMPROVEMENT_WINDOW),
        ]
            
    ], vertical_alignment="bottom", justification="center", element_justification="center", background_color=get_color_arg(), expand_x=True, )

    layout = [
        [c_desc,],
        [sg.pin(c_image_assembly_steps, shrink=True, expand_x=True)],
        [c_canvas],
        [sg.VPush()],
        [bottom_button_bar],
        
    ]
    return layout