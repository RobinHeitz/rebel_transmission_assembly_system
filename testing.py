from can.bus import BusState

from can.interfaces.pcan import PcanBus

from can.interfaces.pcan.basic import (
    PCAN_USBBUS1, PCAN_USBBUS2, PCAN_USBBUS3, PCAN_USBBUS4, PCAN_USBBUS5, PCAN_USBBUS6, 
    PCAN_USBBUS7, PCAN_USBBUS8, PCAN_USBBUS9, PCAN_USBBUS10, PCAN_USBBUS11, PCAN_USBBUS12, 
    PCAN_USBBUS13, PCAN_USBBUS14, PCAN_USBBUS15, PCAN_USBBUS16)

from can.interfaces.pcan.basic import PCANBasic, PCAN_DICT_STATUS, TPCANHandle, TPCANMsg, TPCANTimestamp, PCAN_BAUD_500K, PCAN_MESSAGE_STANDARD
from can.interfaces.pcan.basic import PCAN_ERROR_OK, PCAN_ERROR_XMTFULL, PCAN_ERROR_OVERRUN, PCAN_ERROR_ANYBUSERR, PCAN_ERROR_QRCVEMPTY, PCAN_ERROR_QOVERRUN, PCAN_ERROR_QXMTFULL, PCAN_ERROR_REGTEST

import time

from ctypes import *

messageID = 0x10
std_baudrate = PCAN_BAUD_500K

# PCAN USB Adapter
# Geräte-ID: FFh
# Art.-Nr.: IPEH-002021/002022


all_channels = [
    PCAN_USBBUS1, PCAN_USBBUS2, PCAN_USBBUS3, PCAN_USBBUS4, PCAN_USBBUS5, 
    PCAN_USBBUS6, PCAN_USBBUS7, PCAN_USBBUS8, PCAN_USBBUS9, PCAN_USBBUS10, 
    PCAN_USBBUS11,PCAN_USBBUS12, PCAN_USBBUS13, PCAN_USBBUS14, PCAN_USBBUS15, PCAN_USBBUS16]


def validate_all_channels():
    """Goes through all channels and prints out which channel, e.g. 'PCAN_USBBUS1' is possible to connect to."""
    for c, index in zip(all_channels, list(range(1,100))):
        pcan = PCANBasic()
        status = pcan.Initialize(c, std_baudrate)
        if status != PCAN_ERROR_OK:
            print(f"Init of pcan channel PCAN_USBBUS{index} has failed.")
        else:
            print(f"Init channel PCAN_USBBUS{index} was successful.")

        pcan.Uninitialize(c)

def get_status_description(pcan, channel):
    status, message, timestamp_ = pcan.Read(channel)
    return PCAN_DICT_STATUS.get(status)


def get_status(pcan, channel):
    """Returns current Status.
    Returns status (str), message (TPCANMsg) and a timestamp (TPCANTimestamp)"""
    status, message, timestamp = pcan.Read(channel)
    status = PCAN_DICT_STATUS.get(status)
    return status, message, timestamp
    

def _get_cmd_msg(data, id=messageID):
    """Basic construction of a can message with 8 bytes.
    
    Params:
    data: List of bytes as hex."""
    msg = TPCANMsg()
    msg.DATA = (c_ubyte * 8)()

    for index, data_item in enumerate(data):
        msg.DATA[index] = data_item
    msg.LEN = c_ubyte(len(data))
    msg.MSGTYPE = PCAN_MESSAGE_STANDARD
    msg.ID = id

    return msg


def _write_cmd(pcan, channel, msg, cmd_description=""):
    status = pcan.Write(channel, msg)
    if status == PCAN_ERROR_OK:
        print(f"Status OK: {cmd_description}")
    else:
        raise Exception(f"Status is not OK: {PCAN_DICT_STATUS.get(status)} while {cmd_description}")


def cmd_reset_errors(pcan, channel):
    msg = _get_cmd_msg([0x01, 0x06])
    _write_cmd(pcan, channel, msg, "reset_errors")


def cmd_enable_motor(pcan, channel):
    msg = _get_cmd_msg([0x01, 0x09])
    _write_cmd(pcan, channel, msg, "enable_motors")

def cmd_disable_motor(pcan, channel):
    msg = _get_cmd_msg([0x01, 0x0A])
    _write_cmd(pcan, channel, msg, "disable_motors")


def cmd_velocity_mode(pcan, channel):
    msg = _get_cmd_msg([0x25, 0x0, 0x10])
    _write_cmd(pcan, channel, msg, "enable_motors")



if __name__ == "__main__":

    try:

        validate_all_channels()

        print("STARTING NOW")

        current_channel = PCAN_USBBUS1

        pcan = PCANBasic()
        status = pcan.Initialize(current_channel, std_baudrate)
        
        if status != PCAN_ERROR_OK:
            raise Exception("Initializing failed!")
        else:
            print("Connection was succesfull")


        print("Current status is: ", get_status_description(pcan, current_channel))

        status, message, timestamp = get_status(pcan, current_channel)
        print(f"MessageID: {message.ID}, message-type: {message.MSGTYPE}, message length: {message.LEN}")
        
        cmd_reset_errors(pcan, current_channel)
        
        time.sleep(1)
        cmd_enable_motor(pcan, current_channel)


        time.sleep(1)

        while True:

            cmd_velocity_mode(pcan, current_channel)
            time.sleep(1/50)

    
    except KeyboardInterrupt:
        cmd_disable_motor(pcan, current_channel)
        pcan.Uninitialize(current_channel)

    except Exception as e:
        print(e)
