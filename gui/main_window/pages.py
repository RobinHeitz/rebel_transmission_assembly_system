from turtle import color
import PySimpleGUI as sg

from data_management.model import AssemblyStep
import image_resize
from .definitions import KeyDefs, LayoutTypes
from gui.gui_helpers import Fonts

from typing import Tuple

sg.theme("DarkTeal10")

from gui.gui_helpers import create_btn, get_image, Colors, BtnColors


#####################################################
# LAYOUTS of different 'pages' within the application
#####################################################

config_page = sg.pin(shrink = True, 
    elem=sg.Col(background_color=None, k=KeyDefs.LAYOUT_CONFIG, expand_y=True, layout=[
    
    [
        create_btn("Verbindung herstellen", key=KeyDefs.BTN_CONNECT_CAN, disabled=False), 
        sg.T("Nicht verbunden",auto_size_text= True,  key=KeyDefs.TEXT_CAN_CONNECTED_STATUS, font=Fonts.font_headline, text_color=Colors.yellow),
    ],
    
    [sg.Column(background_color=None, k=KeyDefs.COL_TRANSMISSION_CONFIG ,layout=[
        [
            sg.Text("Getriebegröße", font=Fonts.font_headline),
            sg.Radio("80", default=False, group_id="-radio_transmission_size-",
                     font=Fonts.font_headline, enable_events=True, key=KeyDefs.RADIO_BUTTON_80_CLICKED),
            sg.Radio("105", default=False, group_id="-radio_transmission_size-",
                     font=Fonts.font_headline, enable_events=True, key=KeyDefs.RADIO_BUTTON_105_CLICKED)
        ],
        [
            sg.Checkbox("Absolutwertgeber vorhanden:", default=False, auto_size_text=False,
                        font=Fonts.font_headline, enable_events=True, key=KeyDefs.CHECKBOX_HAS_ENCODER)
        ],
        [
            sg.Checkbox("Bremse vorhanden:", default=False, auto_size_text=False, font=Fonts.font_headline,
                        enable_events=True, disabled=True, key=KeyDefs.CHECKBOX_HAS_BRAKE)
        ],
        
    ])],

    [sg.Col(background_color=None, k=KeyDefs.COL_SOFTWAR_UPDATE, layout=[
        [
            create_btn("Software updaten", key=KeyDefs.BTN_SOFTWARE_UPDATE, disabled=False),
            sg.ProgressBar(max_value=10, size=(20, 50),k=KeyDefs.PROGRESSBAR_SOFTWARE_UPDATE,bar_color=(Colors.yellow, None)),
    ],
    ])],
])),






layout_assembly_step = [
    [
        sg.Col(element_justification="center", vertical_alignment="top", layout=[
            [
                sg.Col(vertical_alignment="top", expand_y=False, layout=[
                    [sg.Multiline("Mein Text", enter_submits=False, auto_size_text=True, enable_events=False, expand_x=True,
                                  write_only=True, size=(None, 6), font=Fonts.font_normal, no_scrollbar=True, expand_y=True, k=KeyDefs.MULTILINE_ASSEMBLY_INSTRUCTION)],
                ]),

                get_image("gui/assembly_pictures/step1.png",
                          size=(300, 300), k=KeyDefs.IMAGE_ASSEMBLY),
            ],
            [sg.HSep(pad=10), ],

            [create_btn("Messung starten", key=KeyDefs.BTN_START_VELO_MODE, )],
            [sg.pin(sg.Canvas(key=KeyDefs.CANVAS_GRAPH_PLOTTING, ),shrink=True)],
            [sg.pin(sg.Text("", font=Fonts.font_headline,key=KeyDefs.TEXT_MIN_MAX_CURRENT_VALUES, visible=False), shrink=True)],

        ]),
        sg.VSeparator(pad=(5, 5, 5, 5,), ),
        sg.Column(vertical_alignment="top", expand_y=False, expand_x = True, layout = [
            [
                sg.pin(
                    sg.Frame("Fehler beheben:", visible=False, k=KeyDefs.FRAME_FAILURE_DETECTION, font=Fonts.font_headline, layout=[
                        
                        [sg.T("Es wurde ein Fehler erkannt: ", k=KeyDefs.TEXT_HIGH_CURRENT_FAILURE_DETECTED,
                                font=Fonts.font_normal, visible=False)],
                        [sg.pin(
                            sg.Col(layout=[
                            [sg.T("Fehler: ", font=Fonts.font_normal)],
                            [sg.Combo(["A", "B", "C"], default_value="B", s=(50, 25), enable_events=True,readonly=True, k=KeyDefs.COMBO_FAILURE_SELECT, font=Fonts.font_normal), ],

                        ], k=KeyDefs.COL_FAILURE_SELECTION_CONTAINER), shrink=True)],
                        [sg.T("Mögliche Maßnahmen:", font=Fonts.font_normal), ],
                        [sg.Listbox([], size=(50, 8), enable_events=False,k=KeyDefs.LISTBOX_POSSIBLE_IMPROVEMENTS, font=Fonts.font_normal), ],
                        [sg.P(), create_btn("Maßnahme anwenden", key=KeyDefs.BTN_SELECT_IMPROVEMENT, disabled=False,button_color=BtnColors.yellow), sg.P()],
                    ]),
                ),
            ],

            # [sg.VPush()],

        ]),
    ],
]

pages_config = {

    (LayoutTypes.config, AssemblyStep.step_1_no_flexring): dict(
        headline="Getriebe Konfigurieren:",

    ),

    (LayoutTypes.assembly, AssemblyStep.step_1_no_flexring): dict(
        headline="Schritt 1: Getriebe ohne Flexring testen",
        image="gui/assembly_pictures/step1.png",
        assembly_instruction = "1) Zuerst wird der Motor mit dem Gehäuseunterteil verschraubt. \n2) Überprüfe, ob der magnetische Polpaarring auf dem Rotor verklebt ist!\n3) Anschließend werden der Encoder mit dem Encoderhalter verklebt und auf die Welle gesteckt.\n4) Die Kabel werden durch die Welle gezogen und mit dem Encoder verbunden, dabei dürfen die Kabel nicht geklemmt oder die Isolierung beschädigt werden!",
    ),

    (LayoutTypes.assembly, AssemblyStep.step_2_with_flexring): dict(
        headline="Schritt 2: Getriebe mit Flexring & Lagerring testen",
        image="gui/assembly_pictures/step2.png",
        assembly_instruction = "Biege das Nadelrollenlager leicht, um es in den Flexring zu stecken. \nAnschließend kann beides zusammen in den Zahnringeinleger gesteckt werden.",

    ),

    (LayoutTypes.assembly, AssemblyStep.step_3_gearoutput_not_screwed): dict(
        headline="Schritt 3: Getriebe mit Abtrieb testen",
        image="gui/assembly_pictures/step3.png",
        assembly_instruction = "Stecke den Abtreib auf. Durch leichtes verdrehen packen die Zähne leichter ineinander.\nWICHTIG: Den Abtrieb nicht schief aufstecken, dadurch können die Kratzer beschädigt werden!",
    ),

}


#######################################################
# HELPER Functions for returning data from pages_config
#######################################################

def get_headline(layout: LayoutTypes, assembly_step: AssemblyStep):
    conf = pages_config.get((layout, assembly_step))
    headline = conf.get("headline")
    return headline

def get_assembly_instruction(layout: LayoutTypes, assembly_step: AssemblyStep):
    conf = pages_config.get((layout, assembly_step))
    headline = conf.get("assembly_instruction")
    return headline


def get_assembly_step_data(layout: LayoutTypes, assembly_step: AssemblyStep):
    ...
    conf = pages_config.get((layout, assembly_step))
    return conf.get("image")


############################################
# Main Layout with navigatin bar at the top
############################################


main_layout = [
    [sg.P(), sg.T("Getriebe konfigurieren:",key="-headline-", font=Fonts.font_headline), sg.P(),],
    
    [sg.HorizontalSeparator(pad=(5, 5, 5, 5,))],

    [sg.Col(expand_x = True, layout=[config_page], element_justification="center")],
    

    # layout_config_page,
    # sg.pin(layout_assembly_step_1, shrink=True),


    # [sg.pin(sg.Column(layout_config_page, key=KeyDefs.LAYOUT_CONFIG, expand_x=True, background_color = "red"), shrink=True)],
    [sg.pin(sg.Column(layout_assembly_step, visible=False, key=KeyDefs.LAYOUT_ASSEMBLY), shrink=True)],
    # Navigation Btns 
    [sg.VP()],
    
    [
        create_btn("Zurück", key=KeyDefs.BTN_NAV_PREVIOUS_PAGE, visible=False),
        create_btn("Fehler hinzufügen",key=KeyDefs.BTN_ADD_FAILURE, button_color=BtnColors.yellow),
        create_btn("Maßnahme hinzufügen",key=KeyDefs.BTN_ADD_IMPROVEMENT, button_color=BtnColors.yellow),
        sg.P(),
        create_btn("Weiter", key=KeyDefs.BTN_NAV_NEXT_PAGE,),
        create_btn("Getriebe ist Ausschuss", key=KeyDefs.BTN_REJECT_TRANSMISSION_NO_IMPROVEMENT, visible=False, button_color=BtnColors.red),
    ],
]


