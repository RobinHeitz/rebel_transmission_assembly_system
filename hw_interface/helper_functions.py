from multiprocessing.sharedctypes import Value
from can.interfaces.pcan.basic import TPCANMsg, PCAN_MESSAGE_STANDARD, TPCANMessageType
from ctypes import *

from .definitions import GEAR_SCALE, RESPONSE_ERROR_CODES_DICT
import time



def get_cmd_msg(data, can_id):
        """Basic construction of a can message with 8 bytes.
        
        Params:
        data: List of bytes as hex.
        data_len: Length of data in bytes"""
        if not 0 <= len(data) <= 8:
            raise ValueError("Length of parameter 'data' is not within [0,8].")
        
        msg = TPCANMsg()
        msg.DATA = (c_ubyte * 8)()

        for index, data_item in enumerate(data):
            msg.DATA[index] = data_item
        msg.LEN = c_ubyte(len(data))
        msg.MSGTYPE = PCAN_MESSAGE_STANDARD
        msg.ID = can_id

        return msg



def int_to_bytes(number, num_bytes=4, signed=True):
    bytes_ = int(number).to_bytes(num_bytes, "big", signed=signed)
    return list(bytes_)


def bytes_to_int(bytes_array, signed=True):
    return int.from_bytes(bytes_array,"big", signed=signed)


def response_error_codes(error_byte):
        """Checks which errors exists based on input error byte.
        
        Returns 2 lists
        - error_descriptions_list: List of short error codes, like 'COM', 'MNE', etc.
        - error_codes_list: Returns list of errors as 'RESPONSE_ERROR_CODES'-type (int)."""
        error_descriptions_list = []
        error_codes_list = []
        for i in range(0,8):
            if error_byte & (1 << i) != 0:
                # if true, error-bit i is active
                error_descriptions_list.append(RESPONSE_ERROR_CODES_DICT.get(i)[0])
                error_codes_list.append(i)
        return error_descriptions_list, error_codes_list

def get_referenced_and_alignment_status(byte):
    """Searches for both flags within movement command reply messages (last byte)
    Returns tuple: referenced, alligned
    """
    can_receive_movement_cmds = byte & (1 << 4) != 0
    alligned = byte & (1 << 6) != 0
    referenced = byte & (1 << 7) != 0
    return referenced, alligned, can_receive_movement_cmds


def pos_from_tics(tics):
    return tics/GEAR_SCALE

def tics_from_pos(pos):
    return pos * GEAR_SCALE