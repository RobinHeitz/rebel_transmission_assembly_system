import PySimpleGUI as sg

from hw_interface.motor_controller import RebelAxisController
from hw_interface.definitions import Exception_Controller_No_CAN_ID, Exception_PCAN_Connection_Failed

from gui.definitions import *
from gui.pages import layout_page_1, layout_page_2, layout_page_3
from gui.plotting import GraphPlotter

from data_management import data_transformation

import logging, time, threading

logFormatter = logging.Formatter("'%(asctime)s - %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.INFO)

fileHandler = logging.FileHandler("gui.log", mode="w")
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)

consolerHandler = logging.StreamHandler()
consolerHandler.setFormatter(logFormatter)
logger.addHandler(consolerHandler)


layout = [

    [
        sg.Column(expand_x=True, element_justification="center",layout=[
        [
            sg.Button("Zurück", k=K_BTN_NAV_PREVIOUS_PAGE,enable_events=True,font=font_normal, disabled=True),
            sg.Push(),
            sg.Text("Getriebe konfigurieren:", key="-headline-", font=font_headline),
            sg.Push(),
            sg.Button("Weiter", key=K_BTN_NAV_NEXT_PAGE, enable_events=True,  font=font_normal),
            ],
        ]),
    ],
    [sg.HorizontalSeparator(pad=(5,5,5,5,))],


    [sg.pin(sg.Column(layout_page_1, expand_x=True, expand_y=True, visible=True, key=K_PAGE_1))],
    [sg.pin(sg.Column(layout_page_2, expand_x=True, expand_y=True, visible=False, key=K_PAGE_2))],
    [sg.pin(sg.Column(layout_page_3, expand_x=True, expand_y=True, visible=False, key=K_PAGE_3))],
    
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


# CONNECT BUTTON
def update_connect_btn_status(status):
    global window
    global controller
    btn = window[K_BTN_CONNECT_CAN]
    txt = window[K_TEXT_CAN_CONNECTED_STATUS]
    
    if status == "PCAN_HW_ERROR":
        btn.update("Verbindung fehlgeschlagen", disabled = True)
        txt.update("Ist der PCAN-Adapter eingesteckt?")
    
    elif status == "FOUND_CAN_ID":
        btn.update("Verbindung herstellen", disabled=True)
        txt.update(f"Verbindung hergestellt: CAN-ID = {hex(controller.can_id)}", text_color="white")

    elif status == "TRY_FIND_CAN_ID":
        btn.update("... Verbinden", disabled=True)
        threading.Thread(target=connect_can_thread, args=(window, controller), daemon=True).start()

    elif status == "ERROR_NO_CAN_ID_FOUND":
        txt.update("Verbindung fehlgeschlagen", text_color="red")
        btn.update("Erneut versuchen", disabled=False)


def connect_can(event, values,controller: RebelAxisController):
    if controller.can_id != None and controller.can_id != -1:
        update_connect_btn_status(status="FOUND_CAN_ID")
    else:
        update_connect_btn_status(status="TRY_FIND_CAN_ID")
    threading.Thread(target=connect_can_thread, args=(window, controller), daemon=True).start()


def connect_can_thread(window, controller:RebelAxisController):
    if controller.can_id != -1:
        update_connect_btn_status(status="FOUND_CAN_ID")
    else:
        board_id = controller.find_can_id(timeout=2)
        if board_id != -1:
            update_connect_btn_status(status="FOUND_CAN_ID")
        else:
            update_connect_btn_status(status="ERROR_NO_CAN_ID_FOUND")



# Software update dummy
def perform_software_update(event, values):
    btn = window[K_BTN_SOFTWARE_UPDATE]
    btn.update(disabled=True)
    threading.Thread(target=perform_software_update_thread, args=(window, controller), daemon=True ).start()

def perform_software_update_thread(window, controller):
    for i in range(1,101):
        time.sleep(.1)
        window.write_event_value(K_SOFTWARE_UPDATE_FEEDBACK, i/10)
    window.write_event_value(K_SOFTWARE_UPDATE_DONE, None)
    

# VELOCITY MODE

def start_velocity_mode(event, values, controller:RebelAxisController):

    global thread_velocity, thread_graph_updater
    thread_graph_updater = threading.Thread(target=graph_update_cycle, args=(window, controller, ), daemon=True)
    thread_graph_updater.start()
    
    controller.start_movement_velocity_mode(duration=5)


def stop_velocity_mode(event, values, controller:RebelAxisController):
    controller.stop_movement_velocity_mode()
    thread_graph_updater.do_plot = False


def graph_update_cycle(window:sg.Window, controller:RebelAxisController):
    """Runs in a thread, ever few seconds it's raising an event for the graphical main queue to trigger graph updating."""
    cur_thread = threading.current_thread()
    while getattr(cur_thread, 'do_plot', True):
        time.sleep(1)
        logger.warning("graph_update_cycle()")

        batch = controller.get_movement_cmd_reply_batch(batchsize=controller.frequency_hz)
        mean_current, pos, millis = data_transformation.sample_data(batch)

        # send value to data controller for adding them into data base :)

        window.write_event_value(K_UPDATE_GRAPH, dict(x=mean_current, y=pos))



def update_graph(event, values, plotter:GraphPlotter):
    """Updates graph. Gets called from a thread running graph_update_cycle()."""
    d = values[event]
    x, y = d.get('x'), d.get('y')
    
    x_data.append(x)
    y_data.append(y)

    plotter.plot_data(x_data, y_data)


######################################################
# FUNCTIONS FOR ENABLING / DISABLING NAVIGATION BUTTONS
######################################################

def _nav_next_page(event, values):
    _hide_current_page()

    global current_page_index
    global page_keys

    current_page_index += 1
    _show_next_page()
    _disable_enable_nav_buttons()


def _nav_previous_page(event, values):
    global current_page_index
    global page_keys
    _hide_current_page()

    current_page_index -= 1
    _show_next_page()
    _disable_enable_nav_buttons()


def _hide_current_page():
    global current_page_index
    global page_keys
    current_page = window[page_keys[current_page_index]]
    current_page.update(visible=False)
    # current_page.hide_row()

def _show_next_page():
    global current_page_index
    global page_keys
    
    next_page = window[page_keys[current_page_index]]
    next_page.update(visible=True)
    # next_page.unhide_row()

def _disable_enable_nav_buttons():
    
    btn_next = window[K_BTN_NAV_NEXT_PAGE]
    btn_prev = window[K_BTN_NAV_PREVIOUS_PAGE]

    btn_prev.update(disabled=False)
    btn_next.update(disabled=False)

    if current_page_index == 0:
        btn_prev.update(disabled=True)
    
    elif current_page_index == len(page_keys) -1:
        btn_next(disabled=True)
 



#################
### MAIN ROUNTINE
#################

if __name__ == "__main__":
    window = sg.Window("ReBeL Getriebe Montage & Kalibrierung", layout, size=(800,500), finalize=True)
    controller = None
    try:
        controller = RebelAxisController(verbose=True)
    except Exception_PCAN_Connection_Failed as e:
        print("Exception PCAN Connection Failed:", e)
        update_connect_btn_status(status="PCAN_HW_ERROR")
    except Exception_Controller_No_CAN_ID:
        ...
        update_connect_btn_status(status="ERROR_NO_CAN_ID_FOUND")

    thread_velocity = None
    thread_graph_updater = None

    page_keys = [K_PAGE_1, K_PAGE_2, K_PAGE_3]
    current_page_index = 0

    graph_plotter = GraphPlotter(window[K_CANVAS_GRAPH_PLOTTING])
    graph_plotter.plot_data([], [])

    x_data, y_data = [],[]

    key_function_map = {
        K_BTN_NAV_NEXT_PAGE: (_nav_next_page, dict()),
        K_BTN_NAV_PREVIOUS_PAGE: (_nav_previous_page, dict()),

        K_RADIO_BUTTON_80_CLICKED: (radio_80_clicked, dict()),
        K_RADIO_BUTTON_105_CLICKED:( radio_105_clicked, dict()),

        K_BTN_CONNECT_CAN: (connect_can, dict(controller=controller)),
        K_BTN_SOFTWARE_UPDATE: (perform_software_update, dict()),

        K_SOFTWARE_UPDATE_FEEDBACK: (lambda event, values: window[K_PROGRESSBAR_SOFTWARE_UPDATE].update_bar(values.get(event)), dict()),
        K_SOFTWARE_UPDATE_DONE : (lambda event, values: window[K_TEXT_SOFTWARE_UPDATE_STATUS_TEXT].update("Software upgedated") , dict()),

        K_BTN_START_VELO_MODE: (start_velocity_mode, dict(controller=controller)),
        K_BTN_STOP_VELO_MODE: (stop_velocity_mode, dict(controller=controller)),
        K_UPDATE_GRAPH: (update_graph, dict(plotter=graph_plotter))



    }
    # Event loop
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Exit'):
            controller.stop_movement()
            controller.shut_down()
            break

        try:
            func, args = key_function_map.get(event)
            func(event, values, **args)
        except Exception as e:
            logger.error(e.__traceback__)
            logger.error(f"WARNING: Missing event in 'key_functin_map': Event = {event} // values = {values.get(event)}")
        
        except KeyboardInterrupt:
            controller.stop_movement()
            controller.shut_down()
            break

    window.close()