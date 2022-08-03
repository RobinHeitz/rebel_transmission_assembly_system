from can.interfaces.pcan.basic import PCAN_USBBUS1
from can.interfaces.pcan.basic import PCANBasic, PCAN_DICT_STATUS, PCAN_BAUD_500K
from can.interfaces.pcan.basic import PCAN_ERROR_OK,PCAN_ERROR_BUSHEAVY, PCAN_ERROR_QRCVEMPTY

import time, logging

from ctypes import *

from .helper_functions import get_cmd_msg, bytes_to_int, int_to_bytes
from .helper_functions import pos_from_tics, tics_from_pos, response_error_codes

from .definitions import RESPONSE_ERROR_CODES, MessageMovementCommandReply, MessageEnvironmentStatus
from .definitions import Exception_PCAN_Connection_Failed, Exception_Controller_No_CAN_ID, Exception_Movement_Command_Reply_Error

from threading import Thread, Lock

logFormatter = logging.Formatter("'%(asctime)s - %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

fileHandler = logging.FileHandler("motor_controller.log", mode="w")
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)



####################
# Class: Controller
####################
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
    motor_env_status_list = []


    def __init__(self, _can_id = None, can_auto_detect = True) -> None:
        self.pcan = PCANBasic()
        status = self.pcan.Initialize(self.channel, self.std_baudrate)
        if status != PCAN_ERROR_OK:
            raise Exception_PCAN_Connection_Failed(self.status_str(status))
        else:
            logger.info("Connection was succesfull")

        if can_auto_detect is True:
            id = self.find_can_id(timeout=2)
            self.can_id = id if id != -1 else None
        else:
            self.can_id = _can_id

        logger.debug("Initializing was succesfull.")
    
    def do_cycle(self):
        time.sleep(self.cycle_time)

    def can_move(self):
        return (self.motor_enabled == True ) and (self.motor_no_err == True)
    

    def stop_movement(self):
        self.cmd_disable_motor()
        self.motor_enabled = False
        self.motor_no_err = False


    def start_msg_listener_thread(self):
        if self.can_id is None or self.can_id == -1:
            raise Exception_Controller_No_CAN_ID("MotorController: No valid CAN-ID is set!")
        self.thread_read_msg = Thread(target=self.read_msg_thread, args=(), daemon=True)
        self.thread_read_msg.start()
        
   
    def read_msg_thread(self):
        while True:
            status, msg, timestamp = self.pcan.Read(self.channel)

            if status == PCAN_ERROR_OK:

                if msg.ID == self.can_id + 1:
                    # Movement cmd answer
                    
                    error_descriptions_list, error_codes_list = response_error_codes(msg.DATA[0])
                    
                    with self.lock:
                        self.movement_cmd_errors = error_descriptions_list
                        if len(error_descriptions_list) == 0:
                            self.motor_no_err = True
                        else:
                            self.motor_no_err = False
                            self.motor_enabled = False

                    logger.info(f"Current Error Codes: {self.movement_cmd_errors}")

                    self.tics = bytes_to_int(msg.DATA[1:5], signed=True)
                    self.pos = pos_from_tics(self.tics)

                    current = bytes_to_int(msg.DATA[5:7], signed=True)
                    if current != 0:
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
                        self.motor_env_status_list.append(m)

              
            
            elif status == PCAN_ERROR_QRCVEMPTY:
                ...
                # logging.error("QUEUE EMPTY")

            elif status == PCAN_ERROR_BUSHEAVY:
                logging.error("*** BUS ERROR - Motor might be off ***")
            
            else: 
                logging.error(f"NEW PCAN ERROR TYPE OCCURED: {status}")
                    

            time.sleep(self.cycle_time)
        

    def find_can_id(self, timeout = 5):
        logger.info("find_can_id()")
        start_time = time.time()

        board_id = -1
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
                    # return board_id
                    break
                else:
                    board_id = -1
        
        self.can_id = board_id
        return board_id



    def shut_down(self):
        self.pcan.Uninitialize(self.channel)

    
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

   
    

if __name__ == "__main__":

    controller = RebelAxisController()
    
