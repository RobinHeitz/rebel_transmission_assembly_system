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



all_channels = [
    PCAN_USBBUS1, PCAN_USBBUS2, PCAN_USBBUS3, PCAN_USBBUS4, PCAN_USBBUS5, 
    PCAN_USBBUS6, PCAN_USBBUS7, PCAN_USBBUS8, PCAN_USBBUS9, PCAN_USBBUS10, 
    PCAN_USBBUS11,PCAN_USBBUS12, PCAN_USBBUS13, PCAN_USBBUS14, PCAN_USBBUS15, PCAN_USBBUS16]


class RebelAxisController:


    def __init__(self) -> None:
        self.can_id = 0x20 # Soldered CAN-ID on motor controller
        self.std_baudrate = PCAN_BAUD_500K
        self.channel = PCAN_USBBUS1
        self.pcan = PCANBasic()

        self.__validate_all_channels()


        status = self.pcan.Initialize(self.channel, self.std_baudrate)
        
        if status != PCAN_ERROR_OK:
            raise Exception(f"Initializing failed! Status = {self.__status_str(status)}")
        else:
            logger.info("Connection was succesfull")
        
        logger.debug("Initializing was succesfull.")

        self.__cmd_reset_position()
        time.sleep(1/50)

        self.__cmd_reset_position()
        time.sleep(1)



    def shut_down(self):
        self.pcan.Uninitialize(self.channel)


    def movement_velocity_mode(self):
        while True:
            self.__cmd_velocity_mode(10)
            has_no_err = self.__read_movement_response_message()

            if not has_no_err:
                self.__cmd_reset_errors()
                time.sleep(1/50)
                self.__cmd_enable_motor()
            time.sleep(1/50)

           
    
    def __validate_all_channels(self):
        """Goes through all channels and prints out which channel, e.g. 'PCAN_USBBUS1' is possible to connect to."""
        for c, index in zip(all_channels, list(range(1,100))):
            pcan = PCANBasic()
            status = pcan.Initialize(c, self.std_baudrate)
            if status != PCAN_ERROR_OK:
                logger.debug(f"Init of pcan channel PCAN_USBBUS{index} has failed.")
            else:
                logger.debug(f"Init channel PCAN_USBBUS{index} was successful.")

            pcan.Uninitialize(c)



    def __get_status(self):
        """Returns current Status.
        Returns status (str), message (TPCANMsg) and a timestamp (TPCANTimestamp)"""
        status, message, timestamp = self.pcan.Read(self.channel)
        return self._status_str(status), message, timestamp
    


    def __get_cmd_msg(self, data, data_len = 8):
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
        msg.ID = self.can_id

        return msg


    def __write_cmd(self, msg, cmd_description):
        status = self.pcan.Write(self.channel, msg)
        if status == PCAN_ERROR_OK:
            return
        else:
            raise Exception(f"Status is not OK! {self.__status_str(status)} while {cmd_description}")


    def __cmd_reset_errors(self):
        logger.debug("cmd_reset_errors()")
        msg = self.__get_cmd_msg([0x01, 0x06])
        self.__write_cmd(msg, "reset_errors")


    def __cmd_enable_motor(self):
        logger.debug("cmd_enable_motor()")
        msg = self.__get_cmd_msg([0x01, 0x09])
        self.__write_cmd(msg, "enable_motors")


    def __cmd_reset_position(self):
        logger.debug("cmd_reset_position()")
        """Needs to be sent 2 times within 20ms at start."""
        msg = self.__get_cmd_msg([0x01, 0x08])
        self.__write_cmd(msg, "reset_position")


    def __cmd_disable_motor(self):
        logger.debug("cmd_disable_motor()")
        msg = self.__get_cmd_msg([0x01, 0x0A])
        self.__write_cmd(msg, "disable_motors")


    def __cmd_allign_rotor(self):
        logger.debug("cmd_allign_rotor()")
        msg = self.__get_cmd_msg([0x01, 0x0C])
        self.__write_cmd(msg, "align_rotor")


    def __cmd_velocity_mode(self, velo=10):
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

        
        msg = self.__get_cmd_msg([0x25, *velo_bytes])
        self.__write_cmd(msg, "velocity_mode")


    def __cmd_position_mode(self, position):
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
        msg = self.__get_cmd_msg([0x14,0x0,*tics_32_bits])    
        self.__write_cmd(msg, "position_mode")


    def __timestamp_str(self, timestamp):
        return f"Timestamps Milliseconds: {timestamp.millis} // Milliseconds (overflow): {timestamp.millis_overflow} // Microseconds: {timestamp.micros}"

    def __status_str(self, status):
        return f"Current Status: {PCAN_DICT_STATUS.get(status)}"

    def __response_error_codes(self, error_byte):
        #check if the 1st bit is in set:
        errors = []
        for i in range(0,8):
            if error_byte & (1 << i) != 0:
                # if true, error-bit i is active
                errors.append(RESPONSE_ERROR_CODES_DICT.get(i)[0])
        return errors


    def __read_movement_response_message(self):
        """Read the response from a movement cmd."""
        
        logger.debug("#"*10)
        logger.debug("__read_movement_response_message()")

        def __read():
            status, msg, timestamp = self.pcan.Read(self.channel)
            return status, msg, timestamp
        
        
        status, msg, timestamp = __read()

        while msg.ID != self.can_id + 1:
            status, msg, timestamp = __read()
        
        logger.debug("Movement cmd response detected.")
        
        data = msg.DATA
        error_codes = self.__response_error_codes(data[0])


        tics = bytes_to_int(data[1:5],signed=True)        
        
        # pos transission [°]
        pos = tics / 1031.111
        logger.info(f"Current Position: {pos} // Tics: {tics}")

        current = bytes_to_int(data[5:7], signed=True)
        logger.info(f"Current: {current}")

        return len(error_codes) == 0
   
   
    def __read_messages(self):
        """
        Reads a message. The answer from a movement command has the CAN-ID = BoardID + 1
        
        """
        logger.debug("#"*10)
        logger.debug("read_messages()")
        status, msg, timestamp = self.pcan.Read(self.channel)

        if msg.ID == self.can_id + 1:
            # answer to movement cmds
            logger.debug("Received msg CAN-ID + 1")
            data = msg.DATA
            
            error_codes = self.__response_error_codes(data[0])
            logging.info(f"Error codes while receiving msg CAN-ID + 1: {error_codes}")

            # tics from motor encoder
            tics = bytes_to_int(data[1:5],signed=True)        
            
            # pos transission [°]
            pos = tics / 1031.111
            logger.info(f"Current Position: {pos} // Tics: {tics}")

            current = bytes_to_int(data[5:7], signed=True)
            logger.info(f"Current: {current}")
        
    
        elif msg.ID == self.can_id + 2:
            # answer to reset error (0x06) cmd / reset position cmd (0x09) / Gear output encoder (Abtriebsencoder/ Absolutwertgeber)
            ...
            logger.debug("Received msg CAN-ID + 2")
            data = msg.DATA

            is_enable_motor_response = True

            if data[0] != 0x06:
                is_enable_motor_response = False
            elif data[1] != 0x0:
                is_enable_motor_response = False
            elif bytes_to_int(data[2:4]) != 0x0109:
                is_enable_motor_response = False
            elif bytes_to_int(data[4:6]) != 0x0001:
                is_enable_motor_response = False
            elif bytes_to_int(data[6:8]) != 0x0000:
                is_enable_motor_response = False
            
            logger.warning(f"SHOULD MOTOR BE ENABLED? {is_enable_motor_response}")
            
        
        elif msg.ID == self.can_id + 3:
            # once a second the controller sends a message voltage, motor temperature and board temperature
            logger.debug("Received msg CAN-ID + 3")
            ...
    
        else:
            logger.debug("Different Msg ID (int):", msg.ID, "and in hex: ", hex(msg.ID))
        

    
    

if __name__ == "__main__":

    controller = RebelAxisController()

    try:
        controller.movement_velocity_mode()

    except KeyboardInterrupt:
        controller.__cmd_disable_motor()
        controller.shut_down()
    
    except Exception as e:
        logging.error(e)
    


    # try:

    #     cmd_reset_position(pcan, current_channel)
    #     time.sleep(1/100)
    #     cmd_reset_position(pcan, current_channel)
        
    #     cmd_reset_errors(pcan, current_channel)
    #     read_messages(pcan, current_channel)
        
    #     time.sleep(1)
    #     cmd_enable_motor(pcan, current_channel)
    #     read_messages(pcan, current_channel)


    #     time.sleep(1)

    #     time_ = time.time()
    #     while time.time() - time_ < 3:

    #         cmd_velocity_mode(pcan, current_channel, velo=10)
    #         read_messages(pcan, current_channel)
    #         time.sleep(1/50)

    #     time.sleep(3)

    #     time_ = time.time()
    #     while time.time() - time_ < 3:

    #         cmd_velocity_mode(pcan, current_channel, velo=-5)
    #         read_messages(pcan, current_channel)
    #         time.sleep(1/50)

      
    
    # except KeyboardInterrupt:
    #     cmd_disable_motor(pcan, current_channel)
    #     pcan.Uninitialize(current_channel)

    # except Exception as e:
    #     print(e)
