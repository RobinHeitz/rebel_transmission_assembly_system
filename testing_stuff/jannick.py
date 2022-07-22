from can.interfaces.pcan.basic import PCANBasic,PCAN_USBBUS1, PCAN_BAUD_500K, PCAN_ERROR_OK
import time

from numpy import sign


def bytes_to_int(bytes_array, signed=True):
    return int.from_bytes(bytes_array,"big", signed=signed)



pcan = PCANBasic()
channel = PCAN_USBBUS1
connect_status = pcan.Initialize(channel, PCAN_BAUD_500K)
can_id = 0x10

if connect_status != PCAN_ERROR_OK:
    print("Connection war nicht möglich.")

else:
    print("Connection erfolgreich.")
    while True:

        status, msg, timestamp = pcan.Read(channel)

        if msg.ID == can_id + 2:
            print("Message mit can_id + 2 gefunden.")
            data = msg.DATA

            if data[0] == 0xEF:
                encoder_pos = bytes_to_int(data[4:8], signed=True)
                print(f"Encoder Position: {encoder_pos}")
            
            elif data[0] == 0xE0:
                motor_error = data[1]
                print(f"Erweiterte Fehlernachricht {motor_error}")
            

        elif msg.ID == can_id + 3:    
            print("Message mit can_id + 3 gefunden.")

        
            milli_voltage = bytes_to_int(data[2:4])
            centi_temp_motor = bytes_to_int(data[4:6])
            centi_temp_board = bytes_to_int(data[6:8])

            print(f"Voltagte = {milli_voltage / 1000}")
            print(f"Motortemperatur = {centi_temp_motor / 100}")
            print(f"Board Temperatur = {centi_temp_board / 100}")
            




        time.sleep(0.5)