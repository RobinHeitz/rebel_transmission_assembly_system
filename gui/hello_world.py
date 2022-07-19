from faulthandler import disable
import PySimpleGUI as sg
import numpy as np

F_RADIO_BUTTON_80_CLICKED = "-FUNCTION_RADIO_BUTTON_80_CLICKED-"
F_RADIO_BUTTON_105_CLICKED = "-FUNCTION_RADIO_BUTTON_105_CLICKED-"
F_BTN_CLICKED = "-FUNCTION_BUTTON_CLICKED-"


def radio_80_clicked():
    checkbox = window[("checkbox", "break_existing")]
    checkbox.update(disabled=True)
    # checkbox.hide_row()

def radio_105_clicked():
    checkbox = window[("checkbox", "break_existing")]
    checkbox.update(disabled=False)
    # checkbox.unhide_row()





function_key_map = {
    F_RADIO_BUTTON_80_CLICKED:radio_80_clicked, 
    F_RADIO_BUTTON_105_CLICKED:radio_105_clicked,
}










# Define the window's contents/ layout

layout_page_1 = [
    [sg.Text("Getriebe konfigurieren:", size=(25,1), key="-headline-", font="Helvetiva 25")],
    
    # [sg.HorizontalSeparator(pad=(10,10,10,10)),],

    [sg.Frame("", layout=[
        [
            sg.Text("Getriebegröße", font="Helvetiva 15"),
            sg.Radio("80", default=True, group_id="-radio_transmission_size-", font="Helvetiva 15", enable_events=True, key=F_RADIO_BUTTON_80_CLICKED), 
            sg.Radio("105", default=False, group_id="-radio_transmission_size-",font="Helvetiva 15", enable_events=True, key=F_RADIO_BUTTON_105_CLICKED)
        ], 

        [
            sg.Checkbox("Encoder vorhanden:", default=True, auto_size_text=False, font="Helvetica 15", key=("checkbox", "encoder_existing") ) 
        ],

        [
            sg.Checkbox("Bremse vorhanden:", default=False, auto_size_text=False, font="Helvetica 15", disabled=True, key=("checkbox", "break_existing")) 
        ],
    ])],
     
     
    ]

layout_page_2 = [
    [sg.Text("Seite2!")]

]


layout = [
    [sg.Column(layout_page_1, visible=True, key="p1", ),],
    [sg.Column(layout_page_2, visible=False, key="p2"),],
]

# Create window
window = sg.Window("ReBeL Getriebe Montage & Kalibrierung", layout, size=(800,500))

# Event loop
while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Exit'):
        break
   
    function_to_execute = function_key_map.get(event)
    function_to_execute()

window.close()