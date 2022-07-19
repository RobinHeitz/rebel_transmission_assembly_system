import PySimpleGUI as sg

from hw_interface.motor_controller import RebelAxisController


L_PAGE_1 = "-LAYOUT_PAGE_1-"
L_PAGE_2 = "-LAYOUT_PAGE_2-"

F_RADIO_BUTTON_80_CLICKED = "-FUNCTION_RADIO_BUTTON_80_CLICKED-"
F_RADIO_BUTTON_105_CLICKED = "-FUNCTION_RADIO_BUTTON_105_CLICKED-"
F_BTN_CONNECT_CAN = "-KEY_BUTTON_CONNECT_CAN-"
F_BTN_NEXT_PAGE = "-KEY_BUTTON_NEXT_PAGE-"



def radio_80_clicked():
    checkbox = window[("checkbox", "break_existing")]
    checkbox.update(disabled=True)
    # checkbox.hide_row()

def radio_105_clicked():
    checkbox = window[("checkbox", "break_existing")]
    checkbox.update(disabled=False)
    # checkbox.unhide_row()

def connect_can(controller):
    print("Connect can")
    controller.connect()

def next_page():
    print("next page")
    prev_layout = window[L_PAGE_1]
    prev_layout.update(visible=False)
    prev_layout.hide_row()

    next_layout = window[L_PAGE_2]
    next_layout.update(visible=True)



# Define the window's contents/ layout

layout_page_1 = [
    [sg.Text("Getriebe konfigurieren:", size=(25,1), key="-headline-", font="Helvetiva 25")],
    
    # [sg.HorizontalSeparator(pad=(10,10,10,10)),],

    [sg.Button("Verbindung herstellen", key=F_BTN_CONNECT_CAN, enable_events=True, size=(20,1))],
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
     
    [sg.Button("Nächste Seite", key=F_BTN_NEXT_PAGE, enable_events=True, size=(20,1))],
     
    ]

layout_page_2 = [
    [sg.Text("Seite2!"), sg.Button("Move Motor", key="-TEST-", enable_events=True)]

]


layout = [
    [sg.Column(layout_page_1, visible=True, key=L_PAGE_1, ),],
    [sg.Column(layout_page_2, visible=False, key=L_PAGE_2),],
]

if __name__ == "__main__":
    window = sg.Window("ReBeL Getriebe Montage & Kalibrierung", layout, size=(800,500))

    controller = RebelAxisController()

    # Event loop
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Exit'):
            break
        
        elif event == F_RADIO_BUTTON_80_CLICKED:
            radio_80_clicked()
        
        elif event == F_RADIO_BUTTON_105_CLICKED:
            radio_105_clicked()
        
        elif event == F_BTN_CONNECT_CAN:
            connect_can(controller)

        elif event  == F_BTN_NEXT_PAGE:
            next_page()

        elif event == "-TEST-":
            controller.movement_velocity_mode()
        
    


    window.close()