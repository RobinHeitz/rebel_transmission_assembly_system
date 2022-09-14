import PySimpleGUI as sg

from data_management.model import AssemblyStep
from gui.gui_helpers import Fonts, ToggleButtonImageData as TI
from .definitions import AddImprovementKeys as Keys

DEFAULT_PROGRESS_BAR_COMPUTE = ('#000000', '#000000')
DarkTeal10 =  {
    "BACKGROUND": "#0d3446", 
    "TEXT": "#d8dfe2", 
    "INPUT": "#71adb5", 
    "TEXT_INPUT": "#000000", 
    "SCROLL": "#71adb5",
    "BUTTON": ("#FFFFFF", "#176d81"), "PROGRESS": DEFAULT_PROGRESS_BAR_COMPUTE, "BORDER": 1, "SLIDER_DEPTH": 0, "PROGRESS_DEPTH": 0,
    "COLOR_LIST": ["#0d3446", "#176d81", "#71adb5", "#d8dfe2"], "DESCRIPTION": ["Grey", "Turquoise", "Winter", "Cold"], },

sg.theme("DarkTeal10")

sub_title_args = dict(
    pad = ((0,0), (25,0)),
    font = Fonts.font_normal,
)



def create_layout():

    return [
        [sg.Text("Maßnahme hinzufügen:", font=Fonts.font_headline,
                 background_color=sg.theme_background_color())],
        [sg.HorizontalSeparator()],

        [sg.Text("Name der Maßnahme", **sub_title_args)],
        [sg.Input(size=(None, 5), font=Fonts.font_normal,
                  k=Keys.INPUT_IMPROVEMENT_TITLE, enable_events=True, expand_x=True)],

        [sg.Text("Beschreibung", **sub_title_args)],
        [sg.Multiline(size=(None, 4), font=Fonts.font_normal,
                      k=Keys.MULTI_LINE_DESCRIPTION, enable_events=True)],

        [sg.Text("Bild der Behebung", **sub_title_args)],
        [  
            sg.Input(expand_x=True, k=Keys.INPUT_FILE_BROWSER_PATH, enable_events=True, disabled=True, background_color="Turquoise"),

            sg.FileBrowse(
            "Bild auswählen", 
            file_types = [("Bild-Dateien (PNG, JPG, etc.)", ".png", ".jpg"),],
            ),



        ],


        [sg.Text("Strom bei Behebung trennen:", **sub_title_args)],
        [
            sg.T("Nicht erforderlich", font=Fonts.font_small),
            sg.Button(image_data=TI.toggle_btn_off, k=Keys.BTN_TOGGLE_CABLE_DISCONNECT, button_color=(
                sg.theme_background_color(), sg.theme_background_color()), border_width=0, metadata=False),
            sg.T("Erforderlich", font=Fonts.font_small),

        ],

        [sg.Text("Montageschritt", **sub_title_args)],
        [sg.Combo(values=[step for step in AssemblyStep], expand_x=True, font=Fonts.font_normal,
                  readonly=True, k=Keys.COMBO_ASSEMBLY_STEP, enable_events=True)],

        [sg.Text("Fehler", **sub_title_args)],
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
