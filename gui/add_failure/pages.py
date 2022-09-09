import PySimpleGUI as sg

from data_management.model import AssemblyStep

from .definitions import AddFailureKeys as Keys

sg.theme("DarkTeal10")



font_headline = "Helvetiva 25"
font_normal = "Helvetica 15"
font_small = "Helvetica 13"


layout = [
    [sg.Text("Fehler hinzufügen:", font=font_headline, background_color=sg.theme_background_color())],
    [sg.HorizontalSeparator()],

    [sg.Text("Beschreibung", font=font_normal)],
    [sg.Multiline(size=(None, 5), font=font_normal, k=Keys.MULTI_LINE_DESCRIPTION, enable_events=True)],

    [sg.Text("Montageschritt", font=font_normal)],
    [sg.Combo(values=[step for step in AssemblyStep], expand_x=True, font=font_normal, readonly=True, k=Keys.COMBO_ASSEMBLY_STEP, enable_events=True)],



    [sg.VPush()],

    [
        sg.Button("Abbrechen", button_color="red", size=(10,1), font=font_normal, k=Keys.BTN_CANCEL_ADD_FAILURE),
        sg.Push(),
        sg.Button("Speichern", button_color=sg.GREENS[3], size=(10,1), font=font_normal, k=Keys.BTN_SAVE_FAILURE, disabled=True),
    ]
]