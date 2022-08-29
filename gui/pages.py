import PySimpleGUI as sg

from data_management.model import AssemblyStep
from .definitions import KeyDefs, font_headline, font_normal, font_small, LayoutPageKeys


#####################################################
# LAYOUTS of different 'pages' within the application
#####################################################

layout_config_page = [

    [sg.Button("Verbindung herstellen", key=KeyDefs.BTN_CONNECT_CAN, enable_events=True, font=font_normal, size=(25,1)), sg.Text("Nicht verbunden", key=KeyDefs.TEXT_CAN_CONNECTED_STATUS, font=font_normal)],
    [sg.Frame("", layout=[
        [
            sg.Text("Getriebegröße", font=font_normal),
            sg.Radio("80", default=True, group_id="-radio_transmission_size-", font=font_normal, enable_events=True, key=KeyDefs.RADIO_BUTTON_80_CLICKED), 
            sg.Radio("105", default=False, group_id="-radio_transmission_size-",font=font_normal, enable_events=True, key=KeyDefs.RADIO_BUTTON_105_CLICKED)
        ], 
        [
            sg.Checkbox("Encoder vorhanden:", default=False, auto_size_text=False, font=font_normal, enable_events=True, key=KeyDefs.CHECKBOX_HAS_ENCODER ) 
        ],
        [
            sg.Checkbox("Bremse vorhanden:", default=False, auto_size_text=False, font=font_normal, enable_events=True,disabled=True, key=KeyDefs.CHECKBOX_HAS_BRAKE) 
        ],
    ])],
    
    [
        sg.Button("Software updaten", key=KeyDefs.BTN_SOFTWARE_UPDATE, enable_events=True, font=font_normal, size=(20,1)), 
        sg.ProgressBar(max_value=10, size=(20,20), k=KeyDefs.PROGRESSBAR_SOFTWARE_UPDATE),
        sg.Text("", k=KeyDefs.TEXT_SOFTWARE_UPDATE_STATUS_TEXT, font=font_normal),
        ],
    [
        sg.B("Bewegung testen", k=KeyDefs.BTN_CHECK_MOVEABILITY, enable_events=True, font=font_normal, size=(20,1))
    ],
    ]


layout_assembly_step_1 = [
    [
        sg.Image("gui/assembly_pictures/step_1_resize.png", size=(300,300)),
        sg.VSeparator(pad=(5,5,5,5,)),
        sg.Column([
            [
                sg.Button("Messung starten",enable_events=True, k=(KeyDefs.BTN_START_VELO_MODE, LayoutPageKeys.layout_assembly_step_1_page) ),
                sg.Button("Abbrechen",enable_events=True, k=(KeyDefs.BTN_STOP_VELO_MODE, LayoutPageKeys.layout_assembly_step_1_page) ),
            ],
            [sg.Canvas(key=(KeyDefs.CANVAS_GRAPH_PLOTTING, LayoutPageKeys.layout_assembly_step_1_page), size=(250,250))],
            [sg.Text("", font=font_normal, key=(KeyDefs.TEXT_MIN_MAX_CURRENT_VALUES, LayoutPageKeys.layout_assembly_step_1_page))],
            
            [sg.Frame("Es wurde ein Fehler erkannt:",layout=[
                [
                    sg.T("Fehler: "), 
                    sg.Combo(["A", "B", "C"], default_value="B", s=(50,25), enable_events=True, readonly=True, k=KeyDefs.COMBO_INDICATOR_SELECT),
                    sg.B("Ursachen anzeigen", k=KeyDefs.BTN_INDICATOR_DETECTION),
                    ],
                
            ], visible=False, k=KeyDefs.FRAME_INDICATOR) ],

            [sg.Frame("Fehlerursache auswählen:", layout=[
                [
                    sg.T("Ursache:"),
                    sg.Listbox([], size=(50,8), enable_events=True, k=KeyDefs.LISTBOX_POSSIBLE_FAILURES, ),
                    sg.B("Fehler beheben", enable_events=True ,k=KeyDefs.BTN_SELECT_FAILURE)
                    ],
            ], visible=False, k=KeyDefs.FRAME_POSSIBLE_FAILURES)],
           
            [sg.Frame("Mögliche Fehlerbehebungen:", layout=[
                [
                    # sg.T("Ursache:"),
                    sg.Listbox([], size=(50,8), enable_events=False, k=KeyDefs.LISTBOX_POSSIBLE_IMPROVEMENTS, ),
                    # sg.B("Fehler beheben", enable_events=True ,k=KeyDefs.BTN_SELECT_FAILURE)
                    ],
            ], visible=False, k=KeyDefs.FRAME_POSSIBLE_IMPROVEMENTS)],

        ])

    ],
]


layout_assembly_step_2 = [
    [
        sg.Image("gui/assembly_pictures/step_2_resize.png", size=(300,300)),
        sg.VSeparator(pad=(5,5,5,5,)),
        sg.Column([
            [
                sg.Button("Messung starten",enable_events=True, k=(KeyDefs.BTN_START_VELO_MODE, LayoutPageKeys.layout_assembly_step_2_page) ),
                sg.Button("Abbrechen",enable_events=True, k=(KeyDefs.BTN_STOP_VELO_MODE, LayoutPageKeys.layout_assembly_step_2_page) ),
            ],
            [sg.Canvas(key=(KeyDefs.CANVAS_GRAPH_PLOTTING, LayoutPageKeys.layout_assembly_step_2_page), )],
            [sg.Text("", font=font_normal, key=(KeyDefs.TEXT_MIN_MAX_CURRENT_VALUES, LayoutPageKeys.layout_assembly_step_2_page))]
])

    ],
]


layout_assembly_step_3 = [
    [
        sg.Image("gui/assembly_pictures/step_3_resize.png", size=(300,300)),
        sg.VSeparator(pad=(5,5,5,5,)),
        sg.Column([
            [
                sg.Button("Messung starten",enable_events=True, k=(KeyDefs.BTN_START_VELO_MODE, LayoutPageKeys.layout_assembly_step_3_page) ),
                sg.Button("Abbrechen",enable_events=True, k=(KeyDefs.BTN_STOP_VELO_MODE, LayoutPageKeys.layout_assembly_step_3_page) ),
            ],
            [sg.Canvas(key=(KeyDefs.CANVAS_GRAPH_PLOTTING, LayoutPageKeys.layout_assembly_step_3_page), )],
            [sg.Text("", font=font_normal, key=(KeyDefs.TEXT_MIN_MAX_CURRENT_VALUES, LayoutPageKeys.layout_assembly_step_3_page))]
])

    ],
]



pages_config = [
    dict(
        headline="Getriebe Konfigurieren:", 
        layout=layout_config_page, 
        layout_key=LayoutPageKeys.layout_config_page,
        visible=True,
        ),
    
    dict(
        headline="Schritt 1: Getriebe ohne Flexring testen", 
        layout=layout_assembly_step_1, 
        layout_key=LayoutPageKeys.layout_assembly_step_1_page,
        visible=False,
        assembly_step = AssemblyStep.step_1_no_flexring,
        ),

    dict(
        headline="Schritt 2: Getriebe mit Flexring & Lagerring testen",
        layout=layout_assembly_step_2,
        layout_key=LayoutPageKeys.layout_assembly_step_2_page,
        visible=False,
        assembly_step = AssemblyStep.step_2_with_flexring, 
        ),
    
    dict(
        headline="Schritt 3: Getriebe mit Abtrieb testen",
        layout=layout_assembly_step_3,
        layout_key=LayoutPageKeys.layout_assembly_step_3_page,
        visible=False,
        assembly_step = AssemblyStep.step_3_gearoutput_not_screwed, 
        ),
]




#######################################################
# HELPER Functions for returning data from pages_config
#######################################################


def get_headline_for_index(index: int):
    return pages_config[index].get("headline", f"Es ist leider ein Fehler aufgetreten: Page-index = {index}")


def render_sub_layouts():
    """Returns a list with each sub-layout (also called page)."""
    return [
        [sg.pin(sg.Column(i.get("layout"), expand_x=True, expand_y=True, visible=i.get("visible"), key=i.get("layout_key")))] for i in pages_config
    ]

def get_page_keys():
    return [i.get("layout_key") for i in pages_config]

def get_page_key_for_index(index:int) -> LayoutPageKeys:
    return pages_config[index].get("layout_key")

def get_assembly_step_for_page_index(index:int) -> AssemblyStep:
    return pages_config[index].get("assembly_step")




############################################
# Main Layout with navigatin bar at the top
############################################
main_layout = [

    [
        sg.Column(expand_x=True, element_justification="center",layout=[
        [
            sg.Button("Zurück", k=KeyDefs.BTN_NAV_PREVIOUS_PAGE,enable_events=True,font=font_normal, disabled=True),
            sg.Push(),
            sg.Text("Getriebe konfigurieren:", key="-headline-", font=font_headline),
            sg.Push(),
            sg.Button("Weiter", key=KeyDefs.BTN_NAV_NEXT_PAGE, enable_events=True,  font=font_normal),
            ],
        ]),
    ],
    [sg.HorizontalSeparator(pad=(5,5,5,5,))],

    *render_sub_layouts(),

]
