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
from definitions import RESPONSE_ERROR_CODES, RESPONSE_ERROR_CODES_DICT


import logging
logFormatter = logging.Formatter("'%(asctime)s - %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

fileHandler = logging.FileHandler("log.log", mode="w")
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)

consolerHandler = logging.StreamHandler()
consolerHandler.setFormatter(logFormatter)
logger.addHandler(consolerHandler)


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
            logger.debug(f"Init of pcan channel PCAN_USBBUS{index} has failed.")
        else:
            logger.debug(f"Init channel PCAN_USBBUS{index} was successful.")

        pcan.Uninitialize(c)

# def get_status_description(pcan, channel):
#     status, message, timestamp_ = pcan.Read(channel)
#     return _status_str(status)


def get_status(pcan, channel):
    """Returns current Status.
    Returns status (str), message (TPCANMsg) and a timestamp (TPCANTimestamp)"""
    status, message, timestamp = pcan.Read(channel)
    return _status_str(status), message, timestamp
    

def _get_cmd_msg(data, data_len = 8, id=can_id):
    """Basic construction of a can message with 8 bytes.
    
    Params:
    data: List of bytes as hex.
    data_len: Length of data in bytes"""
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
    logger.debug("cmd_reset_errors()")
    msg = _get_cmd_msg([0x01, 0x06], data_len=2)
    _write_cmd(pcan, channel, msg, "reset_errors")


def cmd_enable_motor(pcan, channel):
    logger.debug("cmd_enable_motor()")
    msg = _get_cmd_msg([0x01, 0x09])
    _write_cmd(pcan, channel, msg, "enable_motors")


def cmd_reset_position(pcan, channel):
    logger.debug("cmd_reset_position()")
    """Needs to be sent 2 times within 20ms at start."""
    msg = _get_cmd_msg([0x01, 0x08], data_len=4)
    _write_cmd(pcan, channel, msg, "reset_position")


def cmd_disable_motor(pcan, channel):
    logger.debug("cmd_disable_motor()")
    msg = _get_cmd_msg([0x01, 0x0A])
    _write_cmd(pcan, channel, msg, "disable_motors")


def cmd_allign_rotor(pcan, channel):
    logger.debug("cmd_allign_rotor()")
    msg = _get_cmd_msg([0x01, 0x0C])
    _write_cmd(pcan, channel, msg, "align_rotor")


def cmd_velocity_mode(pcan, channel, velo=10):
    """Command for Velocity mode.
    Params:
    pcan: PCANBasic instance
    channel: Current PCANChannel
    velo: Velocity transmission-sided in [°/sec]"""
    
    logger.debug("#"*10)
    logger.debug("cmd_velocity_mode()")
    
    if abs(velo) > 36:
        raise TypeError("Parameter velo should not be greater than 36°/sec!")

    rpm = velo * 50/6
    velo_bytes = int_to_bytes(rpm, 2, True)

    
    msg = _get_cmd_msg([0x25, *velo_bytes])
    _write_cmd(pcan, channel, msg, "velocity_mode")


def cmd_position_mode(pcan, channel, position):
    """Position mode where ticks indicates the angle in degrees.
    Params:
    - pcan: PCANBasic instance
    - channel: Current PCANChannel
    - position: Gear output position in degrees
    """
    logger.debug("#"*10)
    logger.debug("cmd_position_mode")

    tics = 100000
    tics_32_bits = int_to_bytes(tics, num_bytes=4, signed=True)
    msg = _get_cmd_msg([0x14,0x0,*tics_32_bits])    
    _write_cmd(pcan, channel, msg, "position_mode")


def _timestamp_str(timestamp):
    return f"Timestamps Milliseconds: {timestamp.millis} // Milliseconds (overflow): {timestamp.millis_overflow} // Microseconds: {timestamp.micros}"

def _status_str(status):
    return f"Current Status: {PCAN_DICT_STATUS.get(status)}"

def _response_error_codes(error_byte):
    #check if the 1st bit is in set:
    errors = []
    for i in range(0,8):
        if error_byte & (1 << i) != 0:
            # if true, error-bit i is active
            errors.append(RESPONSE_ERROR_CODES_DICT.get(i)[0])

    return errors



def read_messages(pcan, channel):
    """
    Reads a message. The answer from a movement command has the CAN-ID = BoardID + 1
    
    """
    logger.debug("#"*10)
    logger.debug("read_messages()")
    status, msg, timestamp = pcan.Read(channel)

    if msg.ID == can_id + 1:
        # answer to movement cmds
        logger.debug("Received msg CAN-ID + 1")
        data = msg.DATA
        
        error_codes = _response_error_codes(data[0])
        logging.info(f"Error codes while receiving msg CAN-ID + 1: {error_codes}")

        # tics from motor encoder
        tics = bytes_to_int(data[1:5],signed=True)        
        
        # pos transission [°]
        pos = tics / 1031.111
        logger.info(f"Current Position: {pos} // Tics: {tics}")

        current = bytes_to_int(data[5:7], signed=True)
        logger.info(f"Current: {current}")
    
   
    elif msg.ID == can_id + 2:
        # answer to reset error (0x06) cmd / reset position cmd (0x09) / Gear output encoder (Abtriebsencoder/ Absolutwertgeber)
        ...
        logger.debug("Received msg CAN-ID + 2")
    
    elif msg.ID == can_id + 3:
        # once a second the controller sends a message voltage, motor temperature and board temperature
        logger.debug("Received msg CAN-ID + 3")
        ...
   
    else:
        logger.debug("Different Msg ID (int):", msg.ID, "and in hex: ", hex(msg.ID))
    

    
    

if __name__ == "__main__":

    try:

        validate_all_channels()

        logger.info("STARTING NOW")

        current_channel = PCAN_USBBUS1

        pcan = PCANBasic()
        status = pcan.Initialize(current_channel, std_baudrate)
        
        if status != PCAN_ERROR_OK:
            raise Exception(f"Initializing failed! Status = {_status_str(status)}")
        else:
            logger.info("Connection was succesfull")


        cmd_reset_position(pcan, current_channel)
        time.sleep(1/100)
        cmd_reset_position(pcan, current_channel)
        
        cmd_reset_errors(pcan, current_channel)
        read_messages(pcan, current_channel)
        
        time.sleep(1)
        cmd_enable_motor(pcan, current_channel)
        read_messages(pcan, current_channel)


        time.sleep(1)

        time_ = time.time()
        while time.time() - time_ < 3:

            cmd_velocity_mode(pcan, current_channel, velo=10)
            read_messages(pcan, current_channel)
            time.sleep(1/50)

        time.sleep(3)

        time_ = time.time()
        while time.time() - time_ < 3:

            cmd_velocity_mode(pcan, current_channel, velo=-5)
            read_messages(pcan, current_channel)
            time.sleep(1/50)

        time.sleep(3)
        cmd_position_mode(pcan, current_channel, None)

        cmd_reset_errors(pcan, current_channel)
        cmd_enable_motor(pcan, current_channel)

        time.sleep(1)

        while True:
            cmd_position_mode(pcan, current_channel, None)
            read_messages(pcan, current_channel)

    
    except KeyboardInterrupt:
        cmd_disable_motor(pcan, current_channel)
        pcan.Uninitialize(current_channel)

    except Exception as e:
        print(e)
