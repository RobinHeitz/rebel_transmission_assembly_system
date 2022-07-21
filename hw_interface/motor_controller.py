from errno import errorcode
from socket import MsgFlag
from can.interfaces.pcan.basic import (
    PCAN_USBBUS1, PCAN_USBBUS2, PCAN_USBBUS3, PCAN_USBBUS4, PCAN_USBBUS5, PCAN_USBBUS6, 
    PCAN_USBBUS7, PCAN_USBBUS8, PCAN_USBBUS9, PCAN_USBBUS10, PCAN_USBBUS11, PCAN_USBBUS12, 
    PCAN_USBBUS13, PCAN_USBBUS14, PCAN_USBBUS15, PCAN_USBBUS16)

from can.interfaces.pcan.basic import PCANBasic, PCAN_DICT_STATUS, TPCANHandle, TPCANMsg, TPCANTimestamp, PCAN_BAUD_500K, PCAN_MESSAGE_STANDARD
from can.interfaces.pcan.basic import PCAN_ERROR_OK,PCAN_ERROR_BUSHEAVY, PCAN_ERROR_XMTFULL, PCAN_ERROR_OVERRUN, PCAN_ERROR_ANYBUSERR, PCAN_ERROR_QRCVEMPTY, PCAN_ERROR_QOVERRUN, PCAN_ERROR_QXMTFULL, PCAN_ERROR_REGTEST



import time

from ctypes import *

from .calculations import bytes_to_int, int_to_bytes
from .definitions import RESPONSE_ERROR_CODES, RESPONSE_ERROR_CODES_DICT
from .helper_functions import get_cmd_msg

from threading import Thread, Lock

from dataclasses import dataclass


import logging
logFormatter = logging.Formatter("'%(asctime)s - %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

fileHandler = logging.FileHandler("motor_controller.log", mode="w")
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)

# consolerHandler = logging.StreamHandler()
# consolerHandler.setFormatter(logFormatter)
# logger.addHandler(consolerHandler)


GEAR_SCALE = 7424*50/360

all_channels = [
    PCAN_USBBUS1, PCAN_USBBUS2, PCAN_USBBUS3, PCAN_USBBUS4, PCAN_USBBUS5, 
    PCAN_USBBUS6, PCAN_USBBUS7, PCAN_USBBUS8, PCAN_USBBUS9, PCAN_USBBUS10, 
    PCAN_USBBUS11,PCAN_USBBUS12, PCAN_USBBUS13, PCAN_USBBUS14, PCAN_USBBUS15, PCAN_USBBUS16]



@dataclass
class MessageMovementCommandReply:
    """Reply message from movement commands.
    Params:
    - current (mA) : float
    - position (°): float
    - millis: float
    """
    current: float
    position: float
    millis: float

@dataclass
class MessageEnvironmentStatus:
    """
    Environmental message, sent acyclical 1-2 times per sec.
    Params:
    - voltage (V): float
    - temp_motor (°C): float
    - temp_board (°C): float
    - millis: float
    """

    voltage:float 
    temp_motor:float 
    temp_board:float 
    millis: float

    def __init__(self, _voltage, _temp_motor, _temp_board, _millis) -> None:
        self.voltage = _voltage / 1000
        self.temp_motor = _temp_motor / 100 if _temp_motor != -1 else 0
        self.temp_board = _temp_board / 100
        self.millis = _millis




def response_error_codes(error_byte):
        #check if the 1st bit is in set:
        errors = []
        for i in range(0,8):
            if error_byte & (1 << i) != 0:
                # if true, error-bit i is active
                errors.append(RESPONSE_ERROR_CODES_DICT.get(i)[0])
        return errors

def pos_from_tics(tics):
    return tics/GEAR_SCALE

def tics_from_pos(pos):
    return pos * GEAR_SCALE


class RebelAxisController:
    cycle_time  = 1/50
    pos = 0
    tics = 0
    std_baudrate = PCAN_BAUD_500K
    channel = PCAN_USBBUS1
    
    motor_no_err = False
    motor_enabled = False
    motor_referenced = False
    motor_position_is_resetted = False
    motor_rotor_is_aligned = False

    lock = Lock()
    
    movement_cmd_errors = []
    movement_cmd_reply_list = []
    motor_env_status = []


    def __init__(self, _can_id = None, can_auto_detect = True) -> None:
        self.pcan = PCANBasic()
        status = self.pcan.Initialize(self.channel, self.std_baudrate)
        if status != PCAN_ERROR_OK:
            raise Exception(f"Initializing failed! Status = {self.status_str(status)}")
        else:
            logger.info("Connection was succesfull")

        if can_auto_detect is True:
            self.can_id = self.find_can_id(timeout=2)
        else:
            self.can_id = _can_id

        logger.debug("Initializing was succesfull.")




    def start_msg_listener_thread(self):
        if self.can_id is None:
            raise Exception("MotorController: No CAN-ID is set!")
        self.thread_read_msg = Thread(target=self.read_msg_thread, args=(), daemon=True)
        self.thread_read_msg.start()
        
   
    def read_msg_thread(self):
        while True:
            status, msg, timestamp = self.pcan.Read(self.channel)

            if status == PCAN_ERROR_OK:

                if msg.ID == self.can_id + 1:
                    
                    # Movement cmd answer
                    error_codes = response_error_codes(msg.DATA[0])
                    with self.lock:
                        self.movement_cmd_errors = error_codes
                        if len(error_codes) == 0:
                            self.motor_no_err = True
                        else:
                            self.motor_no_err = False
                            self.motor_enabled = False

                    logger.info(f"Current Error Codes: {self.movement_cmd_errors}")

                    self.tics = bytes_to_int(msg.DATA[1:5], signed=True)
                    self.pos = pos_from_tics(self.tics)

                    current = bytes_to_int(msg.DATA[5:7], signed=True)
                    msg = MessageMovementCommandReply(current, self.pos, millis=timestamp.millis)
                    logger.debug(msg)

                    with self.lock:
                        self.movement_cmd_reply_list.append(msg)



                elif msg.ID == self.can_id + 2 and msg.DATA[0] == 0x06:
                    # Antwort auf ResetError, MotorEnable, ZeroPosition, DisableMotor, Referenzierung, AlignRotor

                    differentiate_msg = bytes_to_int(msg.DATA[2:4])
                    
                    if differentiate_msg == 0x0106:
                        # Antwort auf ResetError
                        with self.lock:
                            self.motor_no_err = True
                        logging.error("Motor Errors have been resettet")

                    elif differentiate_msg == 0x0109:
                        # Antwort auf MotorEnable
                        with self.lock:
                            self.motor_enabled = True
                        logging.error("Motor is enabled")
                    
                    elif differentiate_msg == 0x010A:
                        # Antwort auf Motor disable
                        logging.error("Motor is disabled")
                        with self.lock:
                            self.motor_enabled = False
                   
                    elif differentiate_msg == 0x020B:
                        # Antwort auf Referenzierung
                        count_ref = bytes_to_int(msg.DATA[4:6])
                        logging.error(f"Answer to motor referencing: Call No. { count_ref }")
                        with self.lock:
                            if count_ref == 2:
                                self.motor_referenced = True
                            else:
                                self.motor_referenced = False
                    
                    elif differentiate_msg == 0x0108:
                        # Antwort auf Position Reset: Nicht erfolgreich
                        logging.error(f"Failed to reset position.")
                        with self.lock:
                            self.motor_position_is_resetted = False
                    
                    elif differentiate_msg == 0x0208:
                        # Antwort auf Position Reset: Erfolgreich
                        count_reset_posi = bytes_to_int(msg.DATA[4:6])
                        logging.error(f"Reset position, Call No. {count_reset_posi}.")
                        with self.lock:
                            self.motor_position_is_resetted = True if count_reset_posi == 2 else False
                    
                    elif differentiate_msg == 0x020C :
                        # Antwort auf: Align Rotor
                        count_align_rotor= bytes_to_int(msg.DATA[4:6])
                        logging.error(f"Align Rotor, Call No. {count_align_rotor}.")
                        with self.lock:
                            if count_align_rotor == 0x02:
                                self.motor_rotor_is_aligned = True
                            else:
                                self.motor_rotor_is_aligned = False
                
                
                elif msg.ID == self.can_id + 2 and msg.DATA[0] == 0x07:
                    
                    if bytes_to_int(msg.DATA[2:4], signed=True) == 0x020B:
                    # Referenzierung der Achse bereits aktiv
                        logging.error("Motor has finished referencing!")
                        with self.lock:
                            self.motor_referenced = True


                elif msg.ID == self.can_id + 3:
                    # Umgebungsparameter, ca. 1 mal pro Sekunde

                    voltage = bytes_to_int(msg.DATA[2:4], signed=True) #mV
                    temp_motor = bytes_to_int(msg.DATA[4:6], signed=True) #m°C
                    temp_board = bytes_to_int(msg.DATA[6:8], signed=True) #m°C

                    m = MessageEnvironmentStatus(voltage, temp_motor, temp_board, timestamp.millis)
                    logger.warning(m)
                    with self.lock:
                        self.motor_env_status.append(m)

              
            
            elif status == PCAN_ERROR_QRCVEMPTY:
                ...
                # logging.error("QUEUE EMPTY")

            elif status == PCAN_ERROR_BUSHEAVY:
                logging.error("*** BUS ERROR - Motor might be off ***")
            
            else: 
                logging.error(f"NEW PCAN ERROR TYPE OCCURED: {status}")
                    

            time.sleep(self.cycle_time)
        



    # def connect(self, timeout=2):
    #     self.can_id = self.find_can_id(timeout=timeout)

    #     if self.can_id == 0:
    #         return False

    #     self.cmd_reset_position()
    #     time.sleep(self.cycle_time)

    #     self.cmd_reset_position()
    #     # time.sleep(1)

    #     return True


    def find_can_id(self, timeout = 5):
        logger.info("find_can_id()")
        start_time = time.time()

        # Umgebungsparameter 0x12 auf CAN-ID + 3
        while time.time() - start_time < timeout:
            status, msg, _ = self.pcan.Read(self.channel)
            if status == PCAN_ERROR_QRCVEMPTY:
                # Receive queue empty
                ...
            else:
                first_2_bytes = bytes_to_int(msg.DATA[0:2])
                board_id = msg.ID - 3
                if board_id in [0x10, 0x20, 0x30, 0x40, 0x50, 0x60] and first_2_bytes == 0x1200:
                    logger.info(f"Found CAN ID: {board_id} // status = {status} // first 2 bytes = {first_2_bytes}")
                    return board_id

        return 0




    @property 
    def current_pos(self):
        return self._current_pos
    
    @current_pos.setter
    def current_pos(self, newPos):
        self._current_pos = newPos
        logging.info(f"New current_pos set: {newPos}")



    def shut_down(self):
        self.pcan.Uninitialize(self.channel)

    
    
    # def movement_velocity_mode(self):
    #     while True:
    #         self.cmd_velocity_mode(10)
    #         has_no_err, pos_degree, current_mA  = self.read_movement_response_message()
    #         self.current_pos = pos_degree

    #         if not has_no_err:
    #             self.cmd_reset_errors()
    #             time.sleep(self.cycle_time)
    #             self.cmd_enable_motor()
    #         time.sleep(self.cycle_time)

    
    # def movement_position_mode(self, to_pos, clock_wise = True, velo=5):
    #     """Moves axis, controlled my position mode.

    #     Params:
    #     - to_pos: Goal position in degrees [0; 360]
    #     - clock_wise: Movement direction (default: True)
    #     - velo: Velocity for movement [degree/ sec]
    #     """
        
    #     increment_degree = velo * self.cycle_time 
    #     s_increment_degree = increment_degree if clock_wise else increment_degree * -1


    #     while abs(self.pos - to_pos) > increment_degree:
    #         self.cmd_position_mode(pos_delta=s_increment_degree)
    #         has_no_err, pos_degree, current_mA  = self.read_movement_response_message()
            
    #         if not has_no_err:
    #             self.cmd_reset_errors()
    #             time.sleep(self.cycle_time)
    #             self.cmd_enable_motor()
            

    #         time.sleep(self.cycle_time)
        
    #     logger.warning(f"Finished Position movement cmd! Current Position = {self.pos}")

           
    
    # def validate_all_channels(self):
    #     """Goes through all channels and prints out which channel, e.g. 'PCAN_USBBUS1' is possible to connect to."""
    #     for c, index in zip(all_channels, list(range(1,100))):
    #         pcan = PCANBasic()
    #         status = pcan.Initialize(c, self.std_baudrate)
    #         if status != PCAN_ERROR_OK:
    #             logger.debug(f"Init of pcan channel PCAN_USBBUS{index} has failed.")
    #         else:
    #             logger.debug(f"Init channel PCAN_USBBUS{index} was successful.")

    #         pcan.Uninitialize(c)


    def write_cmd(self, msg, cmd_description):
        status = self.pcan.Write(self.channel, msg)
        if status == PCAN_ERROR_OK:
            return
        else:
            raise Exception(f"Status is not OK! {self.__status_str(status)} while {cmd_description}")


    def cmd_reset_errors(self):
        logger.debug("cmd_reset_errors()")
        msg = get_cmd_msg([0x01, 0x06], self.can_id)
        self.write_cmd(msg, "reset_errors")


    def cmd_enable_motor(self):
        logger.debug("cmd_enable_motor()")
        msg = get_cmd_msg([0x01, 0x09], self.can_id)
        self.write_cmd(msg, "enable_motors")


    def cmd_reset_position(self):
        logger.debug("cmd_reset_position()")
        """Needs to be sent 2 times within 20ms at start."""
        msg = get_cmd_msg([0x01, 0x08], self.can_id)
        self.write_cmd(msg, "reset_position")
    
    
    def cmd_reference(self):
        logger.debug("cmd_reference()")
        msg = get_cmd_msg([0x01, 0x0B], self.can_id)
        self.write_cmd(msg, "reference")


    def cmd_disable_motor(self):
        logger.debug("cmd_disable_motor()")
        msg = get_cmd_msg([0x01, 0x0A], self.can_id)
        self.write_cmd(msg, "disable_motors")


    def cmd_allign_rotor(self):
        logger.debug("cmd_allign_rotor()")
        msg = get_cmd_msg([0x01, 0x0C], self.can_id)
        self.write_cmd(msg, "align_rotor")

    
    def cmd_velocity_mode(self, velo=10):
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

        
        msg = get_cmd_msg([0x25, *velo_bytes], self.can_id)
        self.write_cmd(msg, "velocity_mode")


    def cmd_position_mode(self, pos_delta):
        """Position mode where ticks indicates the angle in degrees.
        Params:
        - position: Gear output position delta in degrees
        """
        

        logger.debug("#"*10)
        logger.debug("cmd_position_mode")

        newTics = int(round(self.tics + pos_delta * 1031.111,0))
        tics_32_bits = int_to_bytes(newTics, num_bytes=4, signed=True)
        msg = get_cmd_msg([0x14,0x0,*tics_32_bits], self.can_id)    
        self.write_cmd(msg, "position_mode")


    def timestamp_str(self, timestamp):
        return f"Timestamps Milliseconds: {timestamp.millis} // Milliseconds (overflow): {timestamp.millis_overflow} // Microseconds: {timestamp.micros}"

    def status_str(self, status):
        return f"Current Status: {PCAN_DICT_STATUS.get(status)}"

   
    
    # def read_gear_output_encoder(self):
        
    #     logger.debug("#"*10)
    #     logger.debug("__read_movement_response_message()")

    #     def read():
    #         status, msg, timestamp = self.pcan.Read(self.channel)
    #         return status, msg, timestamp


    #     found_gear_output_msg = False
    #     while not found_gear_output_msg:
    #     # while msg.ID != (self.can_id + 2) and msg.DATA[0] != 0xef:
    #         status, msg, timestamp = read()
    #         if msg.ID == (self.can_id + 2) and msg.DATA[0] == 0xef:
    #             found_gear_output_msg = True            
            

    #     data = msg.DATA
    #     logger.info(data[0])
    #     encoder_pos = bytes_to_int(data[4:8], signed=True) / 100
    #     logger.info(f"Encoder absolute position = {encoder_pos}")

    #     return encoder_pos



    # def read_movement_response_message(self):
    #     """Read the response from a movement cmd.
        
    #     Returns tuple of:
    #     - has_no_errors (Boolean)
    #     - position (in degrees)
    #     - current (in mA)"""
        
    #     logger.debug("#"*10)
    #     logger.debug("__read_movement_response_message()")

    #     def read():
    #         status, msg, timestamp = self.pcan.Read(self.channel)
    #         return status, msg, timestamp
        
        
    #     status, msg, timestamp = read()

    #     while msg.ID != self.can_id + 1:
    #         status, msg, timestamp = read()
        
    #     logger.debug("Movement cmd response detected.")
        
    #     data = msg.DATA
    #     error_codes = response_error_codes(data[0])


    #     self.tics = bytes_to_int(data[1:5],signed=True)        
        
    #     # pos transission [°]
    #     self.pos = (self.tics / 1031.111) % 360
    #     logger.warning(f"Current Position: {self.pos} // Tics: {self.tics}")

    #     current = bytes_to_int(data[5:7], signed=True)
    #     logger.info(f"Current: {current}")

    #     return len(error_codes) == 0, self.pos, current
   
   
    # def read_messages(self):
    #     """
    #     Reads a message. The answer from a movement command has the CAN-ID = BoardID + 1
        
    #     """
    #     logger.debug("#"*10)
    #     logger.debug("read_messages()")
    #     status, msg, timestamp = self.pcan.Read(self.channel)

    #     if msg.ID == 1:
    #         logger.warning("Msg.ID == 1")

    #     elif msg.ID == self.can_id + 1:
    #         # answer to movement cmds
    #         logger.debug("Received msg CAN-ID + 1")
    #         data = msg.DATA
            
    #         error_codes = response_error_codes(data[0])
    #         logging.info(f"Error codes while receiving msg CAN-ID + 1: {error_codes}")

    #         # tics from motor encoder
    #         tics = bytes_to_int(data[1:5],signed=True)        
            
    #         # pos transission [°]
    #         pos = tics / 1031.111
    #         logger.info(f"Current Position: {pos} // Tics: {tics}")

    #         current = bytes_to_int(data[5:7], signed=True)
    #         logger.info(f"Current: {current}")
        
    
    #     elif msg.ID == self.can_id + 2:
    #         # answer to reset error (0x06) cmd / reset position cmd (0x09) / Gear output encoder (Abtriebsencoder/ Absolutwertgeber)
    #         ...
    #         logger.debug("Received msg CAN-ID + 2")
    #         data = msg.DATA

    #         is_enable_motor_response = True

    #         if data[0] != 0x06:
    #             is_enable_motor_response = False
    #         elif data[1] != 0x0:
    #             is_enable_motor_response = False
    #         elif bytes_to_int(data[2:4]) != 0x0109:
    #             is_enable_motor_response = False
    #         elif bytes_to_int(data[4:6]) != 0x0001:
    #             is_enable_motor_response = False
    #         elif bytes_to_int(data[6:8]) != 0x0000:
    #             is_enable_motor_response = False
            
    #         logger.warning(f"SHOULD MOTOR BE ENABLED? {is_enable_motor_response}")
            
        
    #     elif msg.ID == self.can_id + 3:
    #         # once a second the controller sends a message voltage, motor temperature and board temperature
    #         logger.debug("Received msg CAN-ID + 3")
    #         ...
    
    #     else:
    #         logger.debug(f"Different Msg ID (int) {msg.ID} and in hex: {hex(msg.ID)}")
        

    
    

if __name__ == "__main__":

    controller = RebelAxisController()

    # try:
    #     ...
    #     # controller.movement_velocity_mode()
    #     controller.movement_position_mode(150, velo=45)
    # except KeyboardInterrupt:
    #     controller.__cmd_disable_motor()
    #     controller.shut_down()
    
    # except Exception as e:
    #     logging.error(e)
    
