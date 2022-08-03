from threading import Thread
from can.interfaces.pcan.basic import PCANBasic,PCAN_USBBUS1, PCAN_BAUD_500K, PCAN_ERROR_OK
import time
from hw_interface.definitions import MessageEnvironmentStatus, MessageMovementCommandReply

from hw_interface.motor_controller import RebelAxisController

import paho.mqtt.client as mqtt 


###########################################
# Using MotorController Class to move motor
###########################################



THING_ID = "4baea65e-9c1f-4791-bc5f-9f781d808f7c"
THING_KEY = "mb53pdj8nf768jxonvf1tx27i527abbw"


def publish_env_data(msg:MessageEnvironmentStatus, client:mqtt.Client):
    print("publish_env_dat()")
    voltage, temp_motor, temp_board, _ = msg()
    client.publish("voltage", voltage)
    client.publish("temp_motor", temp_motor)
    client.publish("temp_board", temp_board)

def publish_motor_stats(msg:MessageMovementCommandReply, client:mqtt.Client):
    print("publish_motor_stats()")
    current, position, _ = msg()
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
    
    client = mqtt.Client(THING_ID)
    client.username_pw_set("thing", THING_KEY)
    client.connect("mqtt.tingg.io") 

    # client.publish("voltage", 123.456)
    
    c = RebelAxisController()
    c.start_msg_listener_thread()
    
    Thread(target=publish_env_data_thread, args=(c, client), daemon=True).start()
    Thread(target=publish_movement_reply_data_thread, args=(c, client), daemon=True).start()
    
    
    try:
        ...

        c.cmd_reset_position()
        c.do_cycle()
        c.cmd_reset_position()
        c.do_cycle()
        c.cmd_reset_errors()
        c.do_cycle()
        c.cmd_enable_motor()
        c.do_cycle()

        while True:
            c.cmd_velocity_mode(10)
            c.do_cycle()
        
        

    
   

    except KeyboardInterrupt:
        ...
        c.stop_movement()



# pcan = PCANBasic()
# channel = PCAN_USBBUS1
# connect_status = pcan.Initialize(channel, PCAN_BAUD_500K)
# can_id = 0x20

# if connect_status != PCAN_ERROR_OK:
#     print("Connection war nicht möglich.")

# else:
#     print("Connection erfolgreich.")
#     while True:

#         status, msg, timestamp = pcan.Read(channel)

#         if msg.ID == can_id + 2:
#             print("Message mit can_id + 2 gefunden.")
#             data = msg.DATA

#             if data[0] == 0xEF:
#                 encoder_pos = bytes_to_int(data[4:8], signed=True)
#                 print(f"Encoder Position: {encoder_pos}")
            
#             elif data[0] == 0xE0:
#                 motor_error = data[1]
#                 print(f"Erweiterte Fehlernachricht {motor_error}")
            

#         elif msg.ID == can_id + 3:    
#             print("Message mit can_id + 3 gefunden.")

        
#             milli_voltage = bytes_to_int(data[2:4])
#             centi_temp_motor = bytes_to_int(data[4:6])
#             centi_temp_board = bytes_to_int(data[6:8])

#             print(f"Voltagte = {milli_voltage / 1000}")
#             print(f"Motortemperatur = {centi_temp_motor / 100}")
#             print(f"Board Temperatur = {centi_temp_board / 100}")
            




#         time.sleep(0.5)