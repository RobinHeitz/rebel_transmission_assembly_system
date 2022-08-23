import threading
import PySimpleGUI as sg
from hw_interface.motor_controller import RebelAxisController
from gui.definitions import KeyDefs


def connect_can(window:sg.Window, controller: RebelAxisController):
    """Invoked when BTN 'Connect CAN' is clicked. Try to connect to CAN-ID if given or find CAN-ID of connected device.
    Params:
    - window (sg.Window): Current PySimpleGUI window instance.
    - controller (RebelAxisController): Working instance of RebelAxisController."""

    if controller.can_id != None and controller.can_id != -1:
        update_connect_btn_status("FOUND_CAN_ID", window,controller)
    else:
        update_connect_btn_status("TRY_FIND_CAN_ID", window, controller)
    threading.Thread(target=connect_can_thread, args=(window, controller,), daemon=True).start()


def connect_can_thread(window:sg.Window, controller:RebelAxisController):
    if controller.can_id != -1:
        update_connect_btn_status("FOUND_CAN_ID", window, controller)
    else:
        board_id = controller.find_can_id(timeout=2)
        if board_id != -1:
            update_connect_btn_status("FOUND_CAN_ID", window, controller)
        else:
            update_connect_btn_status("ERROR_NO_CAN_ID_FOUND", window, controller)



def update_connect_btn_status(status:str, window:sg.Window, controller: RebelAxisController):
    ...
    btn = window[KeyDefs.BTN_CONNECT_CAN]
    txt = window[KeyDefs.TEXT_CAN_CONNECTED_STATUS]
    
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

            