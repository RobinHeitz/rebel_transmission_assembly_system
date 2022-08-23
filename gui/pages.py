import PySimpleGUI as sg
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
    ]


layout_assembly_step_1 = [
    [
        sg.Image("gui/assembly_pictures/step_1_resize.png", size=(300,300)),
        sg.VSeparator(pad=(5,5,5,5,)),
        sg.Column([
            [
                sg.Button("Messung starten",enable_events=True, k=KeyDefs.BTN_START_VELO_MODE),
                sg.Button("Abbrechen",enable_events=True, k=KeyDefs.BTN_STOP_VELO_MODE),
            ],
            [sg.Canvas(key=KeyDefs.CANVAS_GRAPH_PLOTTING, )],
            [sg.Text("", font=font_normal, key=KeyDefs.TEXT_MIN_MAX_CURRENT_VALUES)]
])

    ],
]




layout_assembly_step_2 = [
    [sg.Text("Seite333!"), sg.Button("Do SomethingS",enable_events=True)],
    
    [ 
        # col_test,
        sg.Image("gui/assembly_pictures/step_1_resize.png", size=(300,300)),
        sg.Image("gui/assembly_pictures/step_2_resize.png", size=(300,300)),
        sg.Image("gui/assembly_pictures/step_3_resize.png", size=(300,300)),
    ],
]



pages_config = [
    dict(
        headline="Getriebe Konfigurieren:", 
        layout=layout_config_page, 
        layout_key=LayoutPageKeys.layout_config_page,
        visible=True,
        # invoke_function_next_btn_clicked = "Test 1A", 
        ),
    
    dict(
        headline="Schritt 1: Getriebe ohne Flexring testen", 
        layout=layout_assembly_step_1, 
        layout_key=LayoutPageKeys.layout_assembly_step_1_page,
        visible=False,
        # invoke_function_next_btn_clicked = "Test 2A", 
        ),

    dict(
        headline="Schritt 2: Getriebe mit Flexring & Lagerring testen",
        layout=layout_assembly_step_2,
        layout_key=LayoutPageKeys.layout_assembly_step_2_page,
        visible=False,
        # invoke_function_next_btn_clicked = "Test 3A", 
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

def get_page_key_for_index(index:int):
    return pages_config[index].get("layout_key")

# def get_navigation_methods_for_index(index:int):
#     return pages_config[index].get("invoke_function_next_btn_clicked")




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
