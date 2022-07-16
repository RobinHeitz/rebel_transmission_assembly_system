from can.bus import BusState

from can.interfaces.pcan import PcanBus

from can.interfaces.pcan.basic import PCAN_USBBUS1, PCAN_USBBUS2, PCAN_USB
from can.interfaces.pcan.basic import PCANBasic, PCAN_DICT_STATUS, TPCANHandle, TPCANMsg, TPCANTimestamp, PCAN_BAUD_500K, PCAN_MESSAGE_STANDARD
from can.interfaces.pcan.basic import PCAN_ERROR_OK, PCAN_ERROR_XMTFULL, PCAN_ERROR_OVERRUN, PCAN_ERROR_ANYBUSERR, PCAN_ERROR_QRCVEMPTY, PCAN_ERROR_QOVERRUN, PCAN_ERROR_QXMTFULL, PCAN_ERROR_REGTEST

import time

from ctypes import *

messageID = 0x10

# PCAN USB Adapter
# Geräte-ID: FFh
# Art.-Nr.: IPEH-002021/002022

# MotorController (nach CPR Data sheet):
# 500k Baudrate/ 20-100Hz Kommunikationsfrequenz 


def position_cmd():
    # 0x14
    pass

def velocity_cmd():
    
    # 0x25
    # 16bit Geschiwndigkeit als int16
    pass


if __name__ == "__main__":
    
    pcan_channel = PCAN_USBBUS1
    baudrate = PCAN_BAUD_500K

    pcan = PcanBus("PCAN_USBBUS1", state=BusState.ACTIVE)
    print("Init PcanBus. Status: ", pcan.status_string())


    reset_status = pcan.reset()
    print("Reset successfull?: ", reset_status)

    print("device number: ", pcan.get_device_number())


    while True:

        
        print("status = ",  pcan.status_string())

        pcan._recv_event()

        time.sleep(0.5)
