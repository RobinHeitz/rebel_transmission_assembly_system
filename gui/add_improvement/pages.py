import PySimpleGUI as sg

from data_management.model import AssemblyStep
from gui.gui_helpers import Fonts, ToggleButtonImageData as TI
from .definitions import AddImprovementKeys as Keys

sg.theme("DarkTeal10")


def create_layout():

    return [
        [sg.Text("Maßnahme hinzufügen:", font=Fonts.font_headline,
                 background_color=sg.theme_background_color())],
        [sg.HorizontalSeparator()],

        [sg.Text("Name der Maßnahme", font=Fonts.font_normal)],
        [sg.Input(size=(None, 5), font=Fonts.font_normal,
                  k=Keys.INPUT_IMPROVEMENT_TITLE, enable_events=True, expand_x=True)],

        [sg.Text("Beschreibung", font=Fonts.font_normal)],
        [sg.Multiline(size=(None, 4), font=Fonts.font_normal,
                      k=Keys.MULTI_LINE_DESCRIPTION, enable_events=True)],


        [sg.Text("Strom bei Behebung trennen:", font=Fonts.font_normal)],
        [
            # sg.Push(),
            sg.T("Nicht erforderlich", font=Fonts.font_small),
            sg.Button(image_data=TI.toggle_btn_off, k=Keys.BTN_TOGGLE_CABLE_DISCONNECT, button_color=(
                sg.theme_background_color(), sg.theme_background_color()), border_width=0, metadata=False),
            sg.T("Erforderlich", font=Fonts.font_small),

        ],

        [sg.Text("Montageschritt", font=Fonts.font_normal)],
        [sg.Combo(values=[step for step in AssemblyStep], expand_x=True, font=Fonts.font_normal,
                  readonly=True, k=Keys.COMBO_ASSEMBLY_STEP, enable_events=True)],

        [sg.Text("Fehler", font=Fonts.font_normal)],
        [sg.Listbox(values=[], select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE, k=Keys.LISTBOX_FAILURES,
                    expand_x=True, size=(None, 4), font=Fonts.font_normal, enable_events=True)],


        [sg.VPush()],

        [
            sg.Button("Abbrechen", button_color="red", size=(10, 1),
                      font=Fonts.font_normal, k=Keys.BTN_CANCEL_ADD_IMPROVEMENT),
            sg.Push(),
            sg.Button("Speichern", button_color=sg.GREENS[3], size=(
                10, 1), font=Fonts.font_normal, k=Keys.BTN_SAVE_IMPROVEMENT, disabled=True,),
        ]
    ]
