from can.interfaces.pcan.basic import TPCANMsg, PCAN_MESSAGE_STANDARD
from ctypes import *


def get_cmd_msg(data, can_id):
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
        msg.ID = can_id

        return msg


def int_to_bytes(number, num_bytes=4, signed=True):
    bytes_ = int(number).to_bytes(num_bytes, "big", signed=signed)
    return list(bytes_)


def bytes_to_int(bytes_array, signed=True):
    return int.from_bytes(bytes_array,"big", signed=signed)