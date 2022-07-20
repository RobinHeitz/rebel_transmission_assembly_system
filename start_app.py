import PySimpleGUI as sg

from hw_interface.motor_controller import RebelAxisController

import threading

import time




L_PAGE_1 = "-LAYOUT_PAGE_1-"
L_PAGE_2 = "-LAYOUT_PAGE_2-"

F_RADIO_BUTTON_80_CLICKED = "-FUNCTION_RADIO_BUTTON_80_CLICKED-"
F_RADIO_BUTTON_105_CLICKED = "-FUNCTION_RADIO_BUTTON_105_CLICKED-"
F_BTN_CONNECT_CAN = "-KEY_BUTTON_CONNECT_CAN-"
F_BTN_NEXT_PAGE = "-KEY_BUTTON_NEXT_PAGE-"
F_BTN_TEST = "-TEST-"

E_LONG_OPERATION_UPDATE = "-LONG_OPERATION_UPDATE-"
E_LONG_OPERATION_DONE = "-LONG_OPERATION_DONE-"


def radio_80_clicked(event, values):
    checkbox = window[("checkbox", "break_existing")]
    checkbox.update(disabled=True)
    # checkbox.hide_row()

def radio_105_clicked(event, values):
    checkbox = window[("checkbox", "break_existing")]
    checkbox.update(disabled=False)
    # checkbox.unhide_row()

def connect_can(event, values,controller):
    print("Connect can")
    controller.connect()

def next_page(event, values):
    print("next page")
    prev_layout = window[L_PAGE_1]
    prev_layout.update(visible=False)
    prev_layout.hide_row()

    next_layout = window[L_PAGE_2]
    next_layout.update(visible=True)


def long_operation(event, values, window):
    ...
    threading.Thread(target=long_operation_thread, args=(event, values, window,), daemon=True).start()



def long_operation_thread(event, values, window):
    for i in range(10):
        time.sleep(2)
        print(f"long operation - {i}")
        window.write_event_value(E_LONG_OPERATION_UPDATE, i)
    window.write_event_value(E_LONG_OPERATION_DONE, i)






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
    [sg.Text("Seite2!"), sg.Button("Move Motor", key=F_BTN_TEST, enable_events=True)]

]


layout = [
    [sg.Column(layout_page_1, visible=True, key=L_PAGE_1, ),],
    [sg.Column(layout_page_2, visible=False, key=L_PAGE_2),],
]


def my_test_func(event, values):
    long_operation(window)

def handle_update(event, values):
    print("update long event: ", event, values.get(E_LONG_OPERATION_UPDATE))

def handle_finish(event, values):
    print("MULTITASKING FINISHED", event, values.get(E_LONG_OPERATION_DONE))

if __name__ == "__main__":
    window = sg.Window("ReBeL Getriebe Montage & Kalibrierung", layout, size=(800,500))
    controller = RebelAxisController()

    key_function_map = {
        F_RADIO_BUTTON_80_CLICKED: (radio_80_clicked, dict()),
        F_RADIO_BUTTON_105_CLICKED:( radio_105_clicked, dict()),

        F_BTN_CONNECT_CAN: (connect_can, dict(controller=controller)),
        F_BTN_NEXT_PAGE: (next_page, dict()),
        F_BTN_TEST:  (long_operation, dict(window=window)), 

        E_LONG_OPERATION_UPDATE: (handle_update, dict()),
        E_LONG_OPERATION_DONE: (handle_finish, dict()),



    }
    # Event loop
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Exit'):
            break

        
        func, args = key_function_map.get(event)
        if func is not None and args is not None:
            func(event, values, **args)
        # if func is not None and args is not None:
        #     func(**args)



        # elif event == F_RADIO_BUTTON_80_CLICKED:
        #     radio_80_clicked()
        
        # elif event == F_RADIO_BUTTON_105_CLICKED:
        #     radio_105_clicked()
        
        # elif event == F_BTN_CONNECT_CAN:
        #     connect_can(controller)

        # elif event  == F_BTN_NEXT_PAGE:
        #     next_page()

        # elif event == F_BTN_TEST:
        #     # controller.movement_velocity_mode()
        #     # window.perform_long_operation(long_operation, "-END_OPERATION-")
            
        #     long_operation(window)
        
        # elif event == E_LONG_OPERATION_UPDATE:
        #     print("update long event: ", event, values.get(E_LONG_OPERATION_UPDATE))


        # elif event == E_LONG_OPERATION_DONE:
        #     print("MULTITASKING FINISHED", event, values.get(E_LONG_OPERATION_DONE))
    


    window.close()