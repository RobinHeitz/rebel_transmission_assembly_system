from threading import Thread
import threading
from tkinter import E
from can.interfaces.pcan.basic import PCANBasic,PCAN_USBBUS1, PCAN_BAUD_500K, PCAN_ERROR_OK
import time
import paho.mqtt.client as mqtt 

from hw_interface.definitions import MessageEnvironmentStatus, MessageMovementCommandReply, Exception_Movement_Command_Reply_Error
from hw_interface.motor_controller import RebelAxisController




###########################################
# Using MotorController Class to move motor
###########################################



THING_ID = "4baea65e-9c1f-4791-bc5f-9f781d808f7c"
THING_KEY = "mb53pdj8nf768jxonvf1tx27i527abbw"


def publish_env_data(msg:MessageEnvironmentStatus, client:mqtt.Client):
    if PRINT_PUBLISHING_MSGS == True: print("publish_env_dat()")
    voltage, temp_motor, temp_board, _ = msg()
    client.publish("voltage", voltage)
    client.publish("temp_motor", temp_motor)
    client.publish("temp_board", temp_board)

def publish_motor_stats(msg:MessageMovementCommandReply, client:mqtt.Client):
    if PRINT_PUBLISHING_MSGS == True: print("publish_motor_stats()")
    current, position, tics,  _ = msg()
    client.publish("current", current)
    client.publish("position", position)
    


def publish_env_data_thread(c:RebelAxisController, client:mqtt.Client):
    while True:
        try:
            ...
            env_msg = c.motor_env_status_list.pop()
            publish_env_data(env_msg, client)
            time.sleep(2)
        
        except IndexError:
            ...

def publish_movement_reply_data_thread(c:RebelAxisController, client:mqtt.Client):
    while True:
        try:
            ...
            env_msg = c.movement_cmd_reply_list.pop()
            publish_motor_stats(env_msg, client)
            time.sleep(1)
        
        except IndexError:
            ...
    


if __name__ == "__main__":
    ...
    c = RebelAxisController()
    c.start_msg_listener_thread()

    max_err_reset = 5
    err_reset_counter = 0


    PRINT_PUBLISHING_MSGS = False
    # client = mqtt.Client(THING_ID)
    # client.username_pw_set("thing", THING_KEY)
    # client.connect("mqtt.tingg.io") 
    # Thread(target=publish_env_data_thread, args=(c, client), daemon=True).start()
    # Thread(target=publish_movement_reply_data_thread, args=(c, client), daemon=True).start()

    
    
    try:
        ...
        time.sleep(1)

        print("Start Rotor allignment")
        c.cmd_allign_rotor()
        c.cmd_allign_rotor()

        time.sleep(6)

        print("START Resetting")
        c.cmd_reset_position()
        c.do_cycle()
        c.cmd_reset_position()
        c.do_cycle()


        print("Start moving now")


        delta_tics = 300

        #################
        # WORKIGN EXAMPLE
        #################
        while True:
            try:

                if c.motor_no_err == False:
                    raise Exception_Movement_Command_Reply_Error(c.movement_cmd_errors)

                # c.cmd_position_mode(delta_tics)
                # c.do_cycle()

                c.move_position_mode2(target_pos=90)
            
            except Exception_Movement_Command_Reply_Error:
                print("Exception_Movement_Command_Reply_Error()")
                if max_err_reset >= err_reset_counter:
                    ...
                    c.cmd_reset_errors()
                    c.do_cycle()
                    c.cmd_enable_motor()
                    c.do_cycle()

                    c.tics_setpoint, c.tics_current = 0,0

                    err_reset_counter += 1
                else:
                    c.stop_movement()
                    break



    except KeyboardInterrupt:
        c.stop_movement()
    