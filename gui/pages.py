import PySimpleGUI as sg
from .definitions import *



layout_page_1 = [

    [sg.Button("Verbindung herstellen", key=K_BTN_CONNECT_CAN, enable_events=True, font=font_normal, size=(25,1)), sg.Text("Nicht verbunden", key=K_TEXT_CAN_CONNECTED_STATUS, font=font_normal)],
    [sg.Frame("", layout=[
        [
            sg.Text("Getriebegröße", font=font_normal),
            sg.Radio("80", default=True, group_id="-radio_transmission_size-", font=font_normal, enable_events=True, key=K_RADIO_BUTTON_80_CLICKED), 
            sg.Radio("105", default=False, group_id="-radio_transmission_size-",font=font_normal, enable_events=True, key=K_RADIO_BUTTON_105_CLICKED)
        ], 
        [
            sg.Checkbox("Encoder vorhanden:", default=False, auto_size_text=False, font=font_normal, enable_events=True, key=K_CHECKBOX_HAS_ENCODER ) 
        ],
        [
            sg.Checkbox("Bremse vorhanden:", default=False, auto_size_text=False, font=font_normal, enable_events=True,disabled=True, key=K_CHECKBOX_HAS_BRAKE) 
        ],
    ])],
    
    [
        sg.Button("Software updaten", key=K_BTN_SOFTWARE_UPDATE, enable_events=True, font=font_normal, size=(20,1)), 
        sg.ProgressBar(max_value=10, size=(20,20), k=K_PROGRESSBAR_SOFTWARE_UPDATE),
        sg.Text("", k=K_TEXT_SOFTWARE_UPDATE_STATUS_TEXT, font=font_normal),
        ],
    ]


layout_page_2 = [
    [
        sg.Image("gui/assembly_pictures/step_1_resize.png", size=(300,300)),
        sg.VSeparator(),
        sg.Column([
            [
                sg.Button("Messung starten",enable_events=True, k=K_BTN_START_VELO_MODE),
                sg.Button("Abbrechen",enable_events=True, k=K_BTN_STOP_VELO_MODE),
            ],
    [sg.Canvas(key=K_CANVAS_GRAPH_PLOTTING, )],
])

    ],
]




layout_page_3 = [
    [sg.Text("Seite333!"), sg.Button("Do SomethingS",enable_events=True)],
    
    [ 
        # col_test,
        sg.Image("gui/assembly_pictures/step_1_resize.png", size=(300,300)),
        sg.Image("gui/assembly_pictures/step_2_resize.png", size=(300,300)),
        sg.Image("gui/assembly_pictures/step_3_resize.png", size=(300,300)),
    ],
]