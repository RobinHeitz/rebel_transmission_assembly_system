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

from calculations import bytes_to_int, int_to_bytes


can_id = 0x20 #CAN ID???
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
    return _status_str(status)


def get_status(pcan, channel):
    """Returns current Status.
    Returns status (str), message (TPCANMsg) and a timestamp (TPCANTimestamp)"""
    status, message, timestamp = pcan.Read(channel)
    return _status_str(status), message, timestamp
    

def _get_cmd_msg(data, id=can_id):
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
        return
    else:
        raise Exception(f"Status is not OK! {_status_str(status)} while {cmd_description}")


def cmd_reset_errors(pcan, channel):
    msg = _get_cmd_msg([0x01, 0x06])
    _write_cmd(pcan, channel, msg, "reset_errors")


def cmd_enable_motor(pcan, channel):
    msg = _get_cmd_msg([0x01, 0x09])
    _write_cmd(pcan, channel, msg, "enable_motors")

def cmd_disable_motor(pcan, channel):
    msg = _get_cmd_msg([0x01, 0x0A])
    _write_cmd(pcan, channel, msg, "disable_motors")


def cmd_velocity_mode(pcan, channel, velo=10):
    """Command for Velocity mode.
    Params:
    pcan: PCANBasic instance
    channel: Current PCANChannel
    velo: Velocity transmission-sided in [°/sec]"""
    if abs(velo) > 36:
        raise TypeError("Parameter velo should not be greater than 36°/sec!")

    rpm = velo * 50/6
    velo_bytes = int_to_bytes(rpm, 2, True)

    
    msg = _get_cmd_msg([0x25, *velo_bytes])
    _write_cmd(pcan, channel, msg, "velocity_mode")

def cmd_position_mode(pcan, channel, ticks):
    """Position mode where ticks indicates the angle in degrees."""
    d0 = 0x14
    d1 = None # unused
    # d2, d3, d4, d5 = position in ticks
    d6 = None #timer
    d7 = None # Dout

    msg = _get_cmd_msg([0x14, 0x0, ])
    pass

def _timestamp_str(timestamp):
    return f"Timestamps Milliseconds: {timestamp.millis} // Milliseconds (overflow): {timestamp.millis_overflow} // Microseconds: {timestamp.micros}"

def _status_str(status):
    return f"Current Status: {PCAN_DICT_STATUS.get(status)}"



def read_messages(pcan, channel):
    """
    Reads a message. The answer from a movement command has the CAN-ID = BoardID + 1
    
    """
    status, msg, timestamp = pcan.Read(channel)

    if msg.ID == can_id + 1:
        # received answer to movement cmds
        
        data = msg.DATA
        
        error_code = data[0] #Fehler byte
        print("Error Byte = ", error_code)

        
        #32 bit position [Tics]
        pos1, pos2, pos3, pos4 = data[1],data[2],data[3],data[4]

        # tics from motor encoder
        tics = bytes_to_int(data[1:5],signed=True)        
        
        # pos transission [°]
        pos = tics / 1031.111
        print(f"Current Position: {pos} // Tics: {tics}")

        current = bytes_to_int(data[5:7], signed=True)
        print(f"Current: {current}")


        

    else:
        pass
        print("Different Msg ID (int):", msg.ID, "and in hex: ", hex(msg.ID))
    

    
    

if __name__ == "__main__":

    try:

        validate_all_channels()

        print("STARTING NOW")

        current_channel = PCAN_USBBUS1

        pcan = PCANBasic()
        status = pcan.Initialize(current_channel, std_baudrate)
        
        if status != PCAN_ERROR_OK:
            raise Exception(f"Initializing failed! Status = {_status_str(status)}")
        else:
            print("Connection was succesfull")


        print("Current status is: ", get_status_description(pcan, current_channel))

        status, message, timestamp = get_status(pcan, current_channel)
        print(f"MessageID: {message.ID}, message-type: {message.MSGTYPE}, message length: {message.LEN}")
        
        cmd_reset_errors(pcan, current_channel)
        read_messages(pcan, current_channel)
        
        time.sleep(1)
        cmd_enable_motor(pcan, current_channel)
        read_messages(pcan, current_channel)


        time.sleep(1)

        while True:

            cmd_velocity_mode(pcan, current_channel, velo=36)
            read_messages(pcan, current_channel)
            time.sleep(1/50)

    
    except KeyboardInterrupt:
        cmd_disable_motor(pcan, current_channel)
        pcan.Uninitialize(current_channel)

    except Exception as e:
        print(e)
