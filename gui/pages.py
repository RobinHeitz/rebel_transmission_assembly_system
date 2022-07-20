import PySimpleGUI as sg
from .definitions import *

layout_page_1 = [

    [sg.Button("Verbindung herstellen", key=K_BTN_CONNECT_CAN, enable_events=True, font=font_normal, size=(20,1)), sg.Text("Nicht verbunden", key=K_TEXT_CAN_CONNECTED_STATUS, font=font_normal)],
    [sg.Frame("", layout=[
        [
            sg.Text("Getriebegröße", font=font_normal),
            sg.Radio("80", default=True, group_id="-radio_transmission_size-", font=font_normal, enable_events=True, key=K_RADIO_BUTTON_80_CLICKED), 
            sg.Radio("105", default=False, group_id="-radio_transmission_size-",font=font_normal, enable_events=True, key=K_RADIO_BUTTON_105_CLICKED)
        ], 
        [
            sg.Checkbox("Encoder vorhanden:", default=True, auto_size_text=False, font=font_normal, key=("checkbox", "encoder_existing") ) 
        ],
        [
            sg.Checkbox("Bremse vorhanden:", default=False, auto_size_text=False, font=font_normal, disabled=True, key=("checkbox", "break_existing")) 
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
        sg.Button("Starte Motor",enable_events=True, k=K_BTN_START_VELO_MODE),
        sg.Button("Stoppe Motor",enable_events=True, k=K_BTN_STOP_VELO_MODE),
        ]
]

layout_page_3 = [
    [sg.Text("Seite333!"), sg.Button("Do SomethingS",enable_events=True)]
]