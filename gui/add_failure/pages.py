import PySimpleGUI as sg

from data_management.model import AssemblyStep
from gui.gui_helpers import Fonts

from .definitions import AddFailureKeys as Keys

sg.theme("DarkTeal10")


def create_layout():
    return [
        [sg.Text("Fehler hinzufügen:", font=Fonts.font_headline,
                 background_color=sg.theme_background_color())],
        [sg.HorizontalSeparator()],

        [sg.Text("Beschreibung", font=Fonts.font_normal)],
        [sg.Multiline(size=(None, 5), font=Fonts.font_normal,
                      k=Keys.MULTI_LINE_DESCRIPTION, enable_events=True)],

        [sg.Text("Montageschritt", font=Fonts.font_normal)],
        [sg.Combo(values=[step for step in AssemblyStep], expand_x=True, font=Fonts.font_normal,
                  readonly=True, k=Keys.COMBO_ASSEMBLY_STEP, enable_events=True)],

        [sg.Text("Behebungsmaßnahmen", font=Fonts.font_normal)],
        [sg.Listbox(values=[], select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE, k=Keys.LISTBOX_IMPROVEMENTS,
                    expand_x=True, size=(None, 6), font=Fonts.font_normal, enable_events=True)],


        [sg.VPush()],

        [
            sg.Button("Abbrechen", button_color="red", size=(10, 1),
                      font=Fonts.font_normal, k=Keys.BTN_CANCEL_ADD_FAILURE),
            sg.Push(),
            sg.Button("Speichern", button_color=sg.GREENS[3], size=(
                10, 1), font=Fonts.font_normal, k=Keys.BTN_SAVE_FAILURE, disabled=True,),
        ]
    ]
