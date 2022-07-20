from concurrent.futures import thread
from pydoc import visiblename
from turtle import color
import PySimpleGUI as sg

from hw_interface.motor_controller import RebelAxisController

import threading

import time

# Layout keys
K_PAGE_1 = "-LAYOUT_PAGE_1-"
K_PAGE_2 = "-LAYOUT_PAGE_2-"

# Button keys
K_BTN_NAV_PREVIOUS_PAGE = "-K_BTN_NAV_PREVIOUS_PAGE-"
K_BTN_NAV_NEXT_PAGE = "-K_BTN_NAV_NEXT_PAGE-"


K_RADIO_BUTTON_80_CLICKED = "-FUNCTION_RADIO_BUTTON_80_CLICKED-"
K_RADIO_BUTTON_105_CLICKED = "-FUNCTION_RADIO_BUTTON_105_CLICKED-"
K_BTN_CONNECT_CAN = "-KEY_BUTTON_CONNECT_CAN-"
K_BTN_SOFTWARE_UPDATE = "-KEY_BUTTON_SOFTWARE_UPDATE-"



# Event key from threading (updates, finished etc.)
K_SOFTWARE_UPDATE_FEEDBACK = "-SOFTWARE_UPDATE_FEEDBACK-"
K_SOFTWARE_UPDATE_DONE = "-SOFTWARE_UPDATE_DONE-"


# Element keys (text, etc.)
K_TEXT_CAN_CONNECTED_STATUS = "-TEXT_CAN_CONNECTION_STATUS-"
K_PROGRESSBAR_SOFTWARE_UPDATE = "-PROGRESSBAR_SOFTWARE_UPDATE-"
K_TEXT_SOFTWARE_UPDATE_STATUS_TEXT = "-TEXT_SOFTWARE_UPDATE_STATUS_TEXT-"



######################################
# Define the window's contents/ layout
######################################

font_headline = "Helvetiva 25"
font_normal = "Helvetica 15"
font_small = "Helvetica 13"




# layout_page_1 = [
#     [sg.Text("Getriebe konfigurieren:", size=(25,1), key="-headline-", font=font_headline)],
#     [sg.Button("Verbindung herstellen", key=K_BTN_CONNECT_CAN, enable_events=True, font=font_normal, size=(20,1)), sg.Text("Nicht verbunden", key=K_TEXT_CAN_CONNECTED_STATUS, font=font_normal)],
#     [sg.Frame("", layout=[
#         [
#             sg.Text("Getriebegröße", font=font_normal),
#             sg.Radio("80", default=True, group_id="-radio_transmission_size-", font=font_normal, enable_events=True, key=K_RADIO_BUTTON_80_CLICKED), 
#             sg.Radio("105", default=False, group_id="-radio_transmission_size-",font=font_normal, enable_events=True, key=K_RADIO_BUTTON_105_CLICKED)
#         ], 
#         [
#             sg.Checkbox("Encoder vorhanden:", default=True, auto_size_text=False, font=font_normal, key=("checkbox", "encoder_existing") ) 
#         ],
#         [
#             sg.Checkbox("Bremse vorhanden:", default=False, auto_size_text=False, font=font_normal, disabled=True, key=("checkbox", "break_existing")) 
#         ],
#     ])],
    
#     [
#         sg.Button("Software updaten", key=K_BTN_SOFTWARE_UPDATE, enable_events=True, font=font_normal, size=(20,1)), 
#         sg.ProgressBar(max_value=10, size=(20,20), k=K_PROGRESSBAR_SOFTWARE_UPDATE),
#         sg.Text("", k=K_TEXT_SOFTWARE_UPDATE_STATUS_TEXT, font=font_normal),
#         ],
#         [sg.VPush()],
#         [
#             sg.Push(), sg.Button("Next", k=K_BTN_NEXT_PAGE,  font=font_normal)
#         ],    
#     ]


layout_page_1 = [
    # [sg.Text("Getriebe konfigurieren:", size=(25,1), key="-headline-", font=font_headline)],
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
        # [sg.VPush()],
        # [
        #     sg.Push(), sg.Button("Next", k=K_BTN_NEXT_PAGE,  font=font_normal)
        # ],    
    ]

layout_page_2 = [
    [sg.Text("Seite2!"), sg.Button("Move Motor",enable_events=True)]

]


page_keys = [K_PAGE_1, K_PAGE_2]
current_page_index = 0


layout = [

    [sg.Button("Zurück", k=K_BTN_NAV_PREVIOUS_PAGE,enable_events=True,font=font_normal, visible=True, disabled=True),sg.Text("Getriebe konfigurieren:", size=(25,1), key="-headline-", font=font_headline)],

    [sg.Column(layout_page_1, expand_x=True, expand_y=True, visible=True, key=K_PAGE_1, ),],
    [sg.Column(layout_page_2, expand_x=True, expand_y=True, visible=False, key=K_PAGE_2),],
    
    [sg.VPush()],
    [
        sg.Push(), sg.Button("Weiter", key=K_BTN_NAV_NEXT_PAGE, enable_events=True,  font=font_normal)
    ],    
]


#######################
### FUNCTIONS  ########
#######################


def radio_80_clicked(event, values):
    checkbox = window[("checkbox", "break_existing")]
    checkbox.update(disabled=True)
    # checkbox.hide_row()

def radio_105_clicked(event, values):
    checkbox = window[("checkbox", "break_existing")]
    checkbox.update(disabled=False)
    # checkbox.unhide_row()

def connect_can(event, values,controller):
    btn = window[K_BTN_CONNECT_CAN]
    btn.update("... Verbinden")
    threading.Thread(target=connect_can_thread, args=(window, controller), daemon=True).start()

def connect_can_thread(window, controller):
    result = controller.connect(timeout=5)
    
    
    status_text = window[K_TEXT_CAN_CONNECTED_STATUS]
    if result == True:
        status_text.update(f"Verbindung hergestellt: CAN-ID: {hex(controller.can_id)}")
    else:
        status_text.update("Verbindung fehlgeschlagen", text_color="red")
    btn = window[K_BTN_CONNECT_CAN]
    btn.update("Verbindung herstellen", disabled=True)
    

def perform_software_update(event, values):
    btn = window[K_BTN_SOFTWARE_UPDATE]
    btn.update(disabled=True)
    threading.Thread(target=perform_software_update_thread, args=(window, controller), daemon=True ).start()


def perform_software_update_thread(window, controller):

    for i in range(1,101):
        time.sleep(.1)
        window.write_event_value(K_SOFTWARE_UPDATE_FEEDBACK, i/10)
    window.write_event_value(K_SOFTWARE_UPDATE_DONE, None)
    




def _nav_next_page(event, values):
    global current_page_index
    global page_keys
    _hide_current_page()

    # make next page visible


    next_page_index = current_page_index + 1
    next_page = window[page_keys[next_page_index]]
    next_page.update(visible=True)
    next_page.unhide_row()

    # disable next page button if at end of pages
    if next_page_index == len(page_keys)-1:
        window[K_BTN_NAV_NEXT_PAGE].update(disabled=True)
    
    if next_page_index > 0:
        window[K_BTN_NAV_PREVIOUS_PAGE].update(disabled=False)

    current_page_index = next_page_index


def _nav_previous_page(event, values):
    global current_page_index
    global page_keys
    _hide_current_page()

    # make previous page visible
    next_page_index = current_page_index - 1

    next_page = window[page_keys[next_page_index]]
    next_page.update(visible=True)
    next_page.unhide_row()

    #disable previous button
    if next_page_index == 0:
        window[K_BTN_NAV_PREVIOUS_PAGE].update(disabled=True)
    
    if next_page_index < len(page_keys) -1:
        window[K_BTN_NAV_NEXT_PAGE].update(disabled=False)
    
    current_page_index = next_page_index



def _hide_current_page():
    global current_page_index
    global page_keys
    current_page = window[page_keys[current_page_index]]
    current_page.update(visible=False)
    current_page.hide_row()




#################
### MAIN ROUNTINE
#################

if __name__ == "__main__":
    window = sg.Window("ReBeL Getriebe Montage & Kalibrierung", layout, size=(800,500))
    controller = RebelAxisController()

    key_function_map = {
        K_BTN_NAV_NEXT_PAGE: (_nav_next_page, dict()),
        K_BTN_NAV_PREVIOUS_PAGE: (_nav_previous_page, dict()),

        K_RADIO_BUTTON_80_CLICKED: (radio_80_clicked, dict()),
        K_RADIO_BUTTON_105_CLICKED:( radio_105_clicked, dict()),

        K_BTN_CONNECT_CAN: (connect_can, dict(controller=controller)),
        K_BTN_SOFTWARE_UPDATE: (perform_software_update, dict()),

        K_SOFTWARE_UPDATE_FEEDBACK: (lambda event, values: window[K_PROGRESSBAR_SOFTWARE_UPDATE].update_bar(values.get(event)), dict()),
        K_SOFTWARE_UPDATE_DONE : (lambda event, values: window[K_TEXT_SOFTWARE_UPDATE_STATUS_TEXT].update("Software upgedated") , dict()),




    }
    # Event loop
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Exit'):
            break

        try:
            func, args = key_function_map.get(event)
            func(event, values, **args)
        except Exception as e:
            print(e.__traceback__)
            print(f"WARNING: Missing event in 'key_functin_map': Event = {event} // values = {values.get(event)}")
        

    window.close()