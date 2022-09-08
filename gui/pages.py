from turtle import color
import PySimpleGUI as sg

from data_management.model import AssemblyStep
import image_resize
from .definitions import KeyDefs, font_headline, font_normal, font_small, LayoutPageKeys, ImprovementWindowKeys as Key, Colors
import random

sg.theme("DarkTeal10")

def get_image(path, size, **kwargs):
    data = image_resize.resize_bin_output(path, size)
    return sg.Image(data, size=size, **kwargs)


#####################################################
# LAYOUTS of different 'pages' within the application
#####################################################



layout_config_page = [

    [sg.Button("Verbindung herstellen",button_color=sg.theme_button_color() , key=KeyDefs.BTN_CONNECT_CAN, enable_events=True, font=font_normal, size=(25,1)), sg.Text("Nicht verbunden", key=KeyDefs.TEXT_CAN_CONNECTED_STATUS, font=font_normal)],
    
    # [sg.B("Fehlercodes auslesen", k=KeyDefs.BTN_READ_ERROR_CODES, enable_events=True, size=(25,1), font=font_normal)],
    
    [sg.Frame("",background_color=Colors.bc, layout=[
        [
            sg.Text("Getriebegröße", font=font_normal),
            sg.Radio("80", default=False, group_id="-radio_transmission_size-", font=font_normal, enable_events=True, key=KeyDefs.RADIO_BUTTON_80_CLICKED), 
            sg.Radio("105", default=False, group_id="-radio_transmission_size-",font=font_normal, enable_events=True, key=KeyDefs.RADIO_BUTTON_105_CLICKED)
        ], 
        [
            sg.Checkbox("Absolutwertgeber vorhanden:", default=False, auto_size_text=False, font=font_normal, enable_events=True, key=KeyDefs.CHECKBOX_HAS_ENCODER ) 
        ],
        [
            sg.Checkbox("Bremse vorhanden:", default=False, auto_size_text=False, font=font_normal, enable_events=True,disabled=True, key=KeyDefs.CHECKBOX_HAS_BRAKE) 
        ],
    ])],
    
    [
        sg.Button("Software updaten",button_color=sg.theme_button_color(), key=KeyDefs.BTN_SOFTWARE_UPDATE, enable_events=True, font=font_normal, size=(20,1)), 
        sg.ProgressBar(max_value=10, size=(20,20), k=KeyDefs.PROGRESSBAR_SOFTWARE_UPDATE),
        sg.Text("", k=KeyDefs.TEXT_SOFTWARE_UPDATE_STATUS_TEXT, font=font_normal),
        ],
    ]
    
    



layout_assembly_step_1 = [
    [
        sg.Col(layout=[
            [ get_image("gui/assembly_pictures/step1.png", size=(300,300))],
        ], vertical_alignment="top",background_color=Colors.bc),
        sg.VSeparator(pad=(5,5,5,5,)),
        sg.Column([
            [
                sg.Button("Messung starten",enable_events=True, k=(KeyDefs.BTN_START_VELO_MODE, LayoutPageKeys.layout_assembly_step_1_page) ),
            ],
            [
                sg.Canvas(key=(KeyDefs.CANVAS_GRAPH_PLOTTING, LayoutPageKeys.layout_assembly_step_1_page), size=(250,250)),
                
                
                sg.Frame("Fehler beheben:",background_color=Colors.bc,font=font_headline,layout=[
                    [sg.Col(background_color=Colors.bc, layout=[
                        [sg.T("Fehler: ", font=font_normal)],
                        [sg.Combo(["A", "B", "C"], default_value="B", s=(50,25), enable_events=True, readonly=True, k=KeyDefs.COMBO_FAILURE_SELECT, font=font_normal),],

                    ], k=KeyDefs.COL_FAILURE_SELECTION_CONTAINER)],
                    [sg.T("Mögliche Maßnahmen:", font=font_normal),],
                    [sg.Listbox([], size=(50,8), enable_events=False, k=KeyDefs.LISTBOX_POSSIBLE_IMPROVEMENTS, font=font_normal ),],
                    [sg.B("Maßnahme anwenden", enable_events=True ,k=KeyDefs.BTN_SELECT_IMPROVEMENT, font=font_normal)],
                    
                ], visible=False, k=KeyDefs.FRAME_FAILURE_DETECTION, vertical_alignment="top"),

                ],
            
            [sg.Text("", font=font_normal, key=(KeyDefs.TEXT_MIN_MAX_CURRENT_VALUES, LayoutPageKeys.layout_assembly_step_1_page), visible=False)],
            [sg.T("Es wurde ein Fehler erkannt: ", k=KeyDefs.TEXT_HIGH_CURRENT_FAILURE_DETECTED, font=font_normal, visible=False)],

            
        ],background_color=Colors.bc)

    ],
]


layout_assembly_step_2 = [
    [
        # sg.Image("gui/assembly_pictures/step_2_resize.png", size=(300,300)),
        get_image("gui/assembly_pictures/step2.png", size=(300,300)),
        sg.VSeparator(pad=(5,5,5,5,)),
        sg.Column([
            [
                sg.Button("Messung starten",enable_events=True, k=(KeyDefs.BTN_START_VELO_MODE, LayoutPageKeys.layout_assembly_step_2_page) ),
            ],
            [sg.Canvas(key=(KeyDefs.CANVAS_GRAPH_PLOTTING, LayoutPageKeys.layout_assembly_step_2_page), )],
            [sg.Text("", font=font_normal, key=(KeyDefs.TEXT_MIN_MAX_CURRENT_VALUES, LayoutPageKeys.layout_assembly_step_2_page))]
])

    ],
]


layout_assembly_step_3 = [
    [
        get_image("gui/assembly_pictures/step3.png", size=(300,300)),
        # sg.Image("gui/assembly_pictures/step_3_resize.png", size=(300,300)),
        sg.VSeparator(pad=(5,5,5,5,)),
        sg.Column([
            [
                sg.Button("Messung starten",enable_events=True, k=(KeyDefs.BTN_START_VELO_MODE, LayoutPageKeys.layout_assembly_step_3_page) ),
                # sg.Button("Abbrechen",enable_events=True, k=(KeyDefs.BTN_STOP_VELO_MODE, LayoutPageKeys.layout_assembly_step_3_page) ),
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
COLS_WITH_COLOR = False

def get_color_arg():
    if COLS_WITH_COLOR == True:
        colors = ["red", "blue", "green", "purple", "orange", "brown", "yellow"]
        return random.choice(colors)
    else:
        return None

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
            sg.Button("Zurück", k=KeyDefs.BTN_NAV_PREVIOUS_PAGE,enable_events=True,font=font_normal, disabled=True, visible=False),
            sg.Push(),
            sg.Text("Getriebe konfigurieren:", key="-headline-", font=font_headline),
            sg.Push(),
            sg.Button("Weiter", key=KeyDefs.BTN_NAV_NEXT_PAGE, enable_events=True,  font=font_normal, disabled=True),
            ],
        ]),
    ],
    [sg.HorizontalSeparator(pad=(5,5,5,5,))],

    *render_sub_layouts(),

]


# IMPROVEMENT WINDOW 

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