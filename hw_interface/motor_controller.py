from datetime import date, datetime
import threading
from can.interfaces.pcan.basic import PCAN_USBBUS1
from can.interfaces.pcan.basic import PCANBasic, PCAN_DICT_STATUS, PCAN_BAUD_500K
from can.interfaces.pcan.basic import PCAN_ERROR_OK,PCAN_ERROR_BUSHEAVY, PCAN_ERROR_QRCVEMPTY, PCAN_ERROR_ILLHW

# from gui.main_window.definitions import KeyDefs

# import PySimpleGUI as sg

import time, logging

from ctypes import *

from .helper_functions import get_cmd_msg, bytes_to_int, int_to_bytes
from .helper_functions import pos_from_tics, tics_from_pos, response_error_codes, get_referenced_and_alignment_status

from .definitions import GEAR_SCALE, RESPONSE_ERROR_CODES, ExceptionPcanIllHardware, ExceptionPcanNoCanIdFound, MessageMovementCommandReply, MessageEnvironmentStatus
from .definitions import Exception_PCAN_Connection_Failed, Exception_Controller_No_CAN_ID, Exception_Movement_Command_Reply_Error

from threading import Thread, Lock


from logs.setup_logger import setup_logger
logger = setup_logger("motor_controller")

def function_prints(f):
    def wrap(*args, **kwargs):
        ...
        logger.info(f"--- {f.__name__}() called")
        return f(*args, **kwargs)
    return wrap


####################
# Class: Controller
####################
class RebelAxisController:
    frequency_hz = 20 # Hz --> 50ms intervall time

    tics_current = 0
    tics_setpoint = 0
    
    std_baudrate = PCAN_BAUD_500K
    channel = PCAN_USBBUS1
    
    motor_no_err = False
    motor_enabled = False
    motor_referenced = False
    motor_position_is_resetted = False
    motor_rotor_is_aligned = False
    
    connected = False
    
    lock = Lock()
    
    movement_cmd_errors = []
    movement_cmd_reply_list = []
    motor_env_status_list = []
    # movement_queue = []

    @function_prints
    def __init__(self, _can_id = -1, can_auto_detect = True, verbose = False) -> None:
        """Init of RebelAxisController cls. Automatically starts 'CAN Message listener thread'.
        
        Params:
        - _can_id: CAN ID of axis.
        - can_auto_detect (default True): Autmatically seeks for CAN ID of connected axis.
        - verbose (default False): Logs additional information.
        """
        logger.debug("Start Initializing.")
        # self.__start_movement_queue = start_movement_queue
        self.__verbose = verbose
        self.can_id = _can_id

        logger.debug("End Initializing.")
    
   
    @function_prints
    def connect(self, ):
        self.pcan = PCANBasic()
        status = self.pcan.Initialize(self.channel, self.std_baudrate)
        
        if status == PCAN_ERROR_OK:
            self.can_id = self.find_can_id()
            if self.can_id != -1:
                self.connected = True

            self.start_msg_listener_thread()
            
            # if self.__start_movement_queue == True:
            #     self.start_movement_thread()
        
        if status == PCAN_ERROR_ILLHW:
            self.disconnect()
            raise ExceptionPcanIllHardware()
        logger.info("Connection was succesfull.")

    
    @function_prints
    def disconnect(self):
        """Gets called for user beeing able to unplug adapter and make changes to gear assembly."""
        if hasattr(self, "thread_read_msg"):
            self.thread_read_msg.running = False
        self.pcan.Uninitialize(self.channel)
        self.can_id = -1
        self.motor_enabled = False
        self.motor_no_err = False
        self.connected = False


    def __log_verbose(self, msg):
        if self.__verbose == True:
            logger.debug(msg)

    @function_prints
    def find_can_id(self, timeout = 2):
        start_time = time.time()

        board_id = -1
        # Umgebungsparameter 0x12 auf CAN-ID + 3
        while time.time() - start_time < timeout:
            status, msg, _ = self.pcan.Read(self.channel)
            if status == PCAN_ERROR_QRCVEMPTY:
                # Receive queue empty
                ...
            else:
                # board_id = msg.ID - 3
                can_ids = [0x10, 0x20, 0x30, 0x40, 0x50, 0x60]
                first_2_bytes = bytes_to_int(msg.DATA[0:2])
                
                if msg.ID-3 in can_ids and first_2_bytes == 0x1200:
                    board_id = msg.ID -3
                    logger.debug(f"Found CAN ID: {board_id} // status = {status} // first 2 bytes = {first_2_bytes}")
                    break
                    
                # Catch startup msg (+2)    
                first_5_bytes = bytes_to_int(msg.DATA[0:5])
                if msg.ID - 2 in can_ids and first_5_bytes == 0x0102030400:
                    board_id = msg.ID -2
                    logger.debug(f"Found CAN ID from startup-msg: {board_id} // status = {status} // first 2 bytes = {first_2_bytes}")
                    break
                    

                else:
                    board_id = -1
        
        if board_id == -1:
            raise ExceptionPcanNoCanIdFound()
        

        self.can_id = board_id
        return board_id



    @function_prints
    def shut_down(self):
        self.disconnect()
    
    @function_prints
    def do_cycle(self):
        time.sleep(1 / self.frequency_hz)

    
    @function_prints
    def get_delta_tics_for_output_velo(self, output_velocity):
        """
        Returns delta tics (int) based on wanted output velocity (and cycle time / Frequency)

        output_velocity = frequency[Hz] * delta_tics[Tics] / GearScale
        <=> delta_Tics = output_velocity * GearScale / frequency
        
        Params:
        - output_velocity: Wanted velo of gear output in [° / sec]

        Return: delta tics (int)
        """
        return int(output_velocity * GEAR_SCALE / self.frequency_hz)


    @function_prints
    def can_move(self):
        logger.error(f"motor_enabled = {self.motor_enabled} / motor_no_err = {self.motor_no_err} ")
        return (self.motor_enabled == True ) and (self.motor_no_err == True)
    

    @function_prints
    def stop_movement(self):
        self.cmd_disable_motor()
        self.motor_enabled = False
        self.motor_no_err = False


    @function_prints
    def get_movement_cmd_reply_batch(self, batchsize:int=20):
        """Returns a batch of movement cmd replies with a given batchsize.
        Params:
        - batchsize (default:20): int"""
        batch = self.movement_cmd_reply_list[:batchsize]
        self.movement_cmd_reply_list = self.movement_cmd_reply_list[batchsize:]
        return batch


    ####################################################
    # Movement directly through velocity CMDs / NO QUEUE
    ####################################################

    @function_prints
    def reach_moveability(self):
        ...
        can_move = self.can_move()
        logger.info(f"can_move: {can_move}")
        max_reset = 5
        reset_counter = 0

        while not self.can_move() and reset_counter < max_reset:
            self.cmd_reset_errors()
            self.do_cycle()
            self.cmd_enable_motor()
            self.do_cycle()
            reset_counter += 1
            self.cmd_velocity_mode(0)

    
    @function_prints
    def start_movement_velocity_mode(self, velocity, duration, invoke_stop_function, invoke_error_function):
        """Starts sending movement cmds with velocity-type. After duration [sec], the invoke_stop_function is called.
        Params:
        - duration:(int) in seconds
        - invoke_stop_function: (function) function that is invoked afer movement has finished."""
        self.thread_movement_velo_mode = Thread(target=self.__movement_velocity_mode, args=(velocity, duration, invoke_stop_function, invoke_error_function), daemon=True)
        self.thread_movement_velo_mode.start()
        
    
    def stop_movement_velocity_mode(self):
        logging.info("stop_movement_velocity")
        self.thread_movement_velo_mode.abort = True
        self.stop_movement()
    

    @function_prints
    def __movement_velocity_mode(self, velocity, duration, invoke_stop_function, invoke_error_function):
        current_thread = threading.current_thread()
        can_move_ = self.can_move()

        logger.info(f"can_move: {can_move_}")
        if not self.can_move():
            self.cmd_reset_errors()
            self.do_cycle()
            self.cmd_enable_motor()
            self.do_cycle()
        
        start_time = datetime.now()

        mne_counter = 0
        
        while getattr(current_thread, "abort", False) == False and (datetime.now() - start_time).total_seconds() < duration:
            self.cmd_velocity_mode(velocity)
            self.do_cycle()

            if "OC" in self.movement_cmd_errors:
                self.stop_movement()
                invoke_error_function("OC")
                return
            
            elif "MNE" in self.movement_cmd_errors and mne_counter <= 5:
                logger.debug("+++")
                logger.debug("MNE, therefore try to reset manually again.")
                self.cmd_reset_errors()
                self.do_cycle()
                self.cmd_reset_errors()
                self.do_cycle()
                self.cmd_enable_motor()
                mne_counter += 1

        self.stop_movement()
        invoke_stop_function()



    ##################################
    ### Read CAN Messages in a thread.
    ##################################


    @function_prints
    def start_msg_listener_thread(self):
        if self.can_id is None or self.can_id == -1:
            raise Exception_Controller_No_CAN_ID("MotorController: No valid CAN-ID is set!")
        self.thread_read_msg = Thread(target=self.read_msg_thread, args=(), daemon=True)
        self.thread_read_msg.start()

        
   
    @function_prints
    def read_msg_thread(self):
        cur_t = threading.current_thread()
        while True and getattr(cur_t, "running", True):
            status, msg, timestamp = self.pcan.Read(self.channel)

            if status == PCAN_ERROR_OK:

                
                ##############################
                ### RECEIVED MSG ON CAN-ID + 1
                ##############################
                if msg.ID == self.can_id + 1:
                    # Movement cmd answer
                    
                    error_descriptions_list, error_codes_list = response_error_codes(msg.DATA[0])
                    referenced, alligned, can_receive_movement_cmds = get_referenced_and_alignment_status(msg.DATA[7])
                    logger.debug(f"Current Error Codes: {error_descriptions_list} | Referenced: {referenced} | alligned: {alligned} | Can receive Movement cmds: {can_receive_movement_cmds}")

                    _tics_current = bytes_to_int(msg.DATA[1:5], signed=True)
                    pos = round(pos_from_tics(_tics_current),2)
                    current = bytes_to_int(msg.DATA[5:7], signed=True)
                    
                    msg = MessageMovementCommandReply(current, pos,_tics_current, millis=timestamp.millis)
                    logger.debug(msg)
                    logger.debug(f"Current Tics: {_tics_current} / Tics setpoint: {self.tics_setpoint} / Lag: {abs(self.tics_setpoint - _tics_current)}")

                    with self.lock:
                        self.movement_cmd_errors = error_descriptions_list
                        self.movement_cmd_reply_list.append(msg)
                        self.tics_current = _tics_current

                        
                        if len(error_descriptions_list) == 0:
                            self.motor_no_err = True
                        else:
                            self.motor_no_err = False
                            self.motor_enabled = False



                ##############################
                ### RECEIVED MSG ON CAN-ID + 2
                ##############################
                elif msg.ID == self.can_id + 2:
                    
                    if msg.DATA[0] == 0x06:
                        differentiate_msg = bytes_to_int(msg.DATA[2:4])
                        # logger.debug(f"CAN-ID + 2: Differentiate MSG based on Bytes 2-4: {hex(differentiate_msg)}")
                        
                        if differentiate_msg == 0x0106:
                            # Antwort auf ResetError
                            with self.lock:
                                self.motor_no_err = True
                            logging.error("Motor Errors have been resettet")

                        elif differentiate_msg == 0x0109:
                            # Antwort auf MotorEnable
                            flag = bytes_to_int(msg.DATA[4:6])
                            with self.lock:
                                self.motor_enabled = True
                            logging.error(f"Motor is enabled / {hex(flag)}")
                        
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
                            ...
                            # Antwort auf Position Reset CMD, unabhängig von Erfolg oder nicht
                            logging.error(f"Received reply: Reset_Position")
                        
                        elif differentiate_msg == 0x0208:
                            # Antwort auf Position Reset: Erfolgreich
                            count_reset_posi = bytes_to_int(msg.DATA[4:6])
                            logging.error(f"Reset position, Call No. {count_reset_posi} at time: {timestamp.millis}.")
                            with self.lock:
                                if count_reset_posi == 2:
                                    self.motor_position_is_resetted = True 
                        
                        elif differentiate_msg == 0x020C :
                            # Antwort auf: Align Rotor
                            count_align_rotor= bytes_to_int(msg.DATA[4:6])
                            logging.error(f"Align Rotor, Call No. {count_align_rotor}.")
                            with self.lock:
                                if count_align_rotor == 0x02:
                                    self.motor_rotor_is_aligned = True
                                else:
                                    self.motor_rotor_is_aligned = False
                    
                    elif msg.DATA[0] == 0x07:
                        if bytes_to_int(msg.DATA[2:4], signed=True) == 0x020B:
                        # Referenzierung der Achse bereits aktiv
                            logging.error("Motor has finished referencing!")
                            with self.lock:
                                self.motor_referenced = True
                    
                    elif msg.DATA[0] == 0xE0:

                        self.__log_verbose("**************************")
                        self.__log_verbose("Erweiterte Fehlernachricht!")

                        motor_error_byte = msg.DATA[1]
                        # bits: Motor n.C. / OC RMS / OC Single Phase / Over Temperature
                        
                        adc_error_byte = msg.DATA[2]
                        # ADC Offset
                        
                        rebel_error = msg.DATA[3]
                        # Com Error / Out of Range
                        
                        control_error = msg.DATA[4]
                        # Velocity High / Low Allign / Parameter Fault

                        self.__log_verbose(f"MotorError: {motor_error_byte} / ADC Error: {adc_error_byte} / Rebel Error: {rebel_error} / Control Error: {control_error}")
                        self.__log_verbose("**************************")
                    
                    
                    elif msg.DATA[0] == 0xEF:
                        ...
                        pos_degree = bytes_to_int(msg.DATA[4:8]) / 100
                        logger.debug(f"Abtriebsencoder Position: {pos_degree}")
                    

                
                ##############################
                ### RECEIVED MSG ON CAN-ID + 3
                ##############################
                elif msg.ID == self.can_id + 3:
                    # Umgebungsparameter, ca. 1 mal pro Sekunde
                    voltage = bytes_to_int(msg.DATA[2:4], signed=True) #mV
                    temp_motor = bytes_to_int(msg.DATA[4:6], signed=True) #m°C
                    temp_board = bytes_to_int(msg.DATA[6:8], signed=True) #m°C

                    m = MessageEnvironmentStatus(voltage, temp_motor, temp_board, timestamp.millis)
                    with self.lock:
                        self.motor_env_status_list.append(m)
                    if self.__verbose == True:
                        logger.warning(m)

              
            
            elif status == PCAN_ERROR_QRCVEMPTY:
                ...
                # logging.error("QUEUE EMPTY")

            elif status == PCAN_ERROR_BUSHEAVY:
                logging.error("*** BUS ERROR - Motor might be off ***")
            
            else: 
                logging.error(f"NEW PCAN ERROR TYPE OCCURED: {status}")
                    
            # Intervall of reading messages: 10 ms 
            time.sleep(1/100)
        


    



    ######################
    ### Send CAN Messages
    ######################


    @function_prints
    def write_cmd(self, msg, cmd_description):
        status = self.pcan.Write(self.channel, msg)
        if status == PCAN_ERROR_OK:
            return
        else:
            if self.connected:
                raise Exception(f"Status is not OK! {self.status_str(status)} while {cmd_description}")


    @function_prints
    def cmd_reset_errors(self):
        msg = get_cmd_msg([0x01, 0x06], self.can_id)
        self.write_cmd(msg, "reset_errors")


    @function_prints
    def cmd_enable_motor(self):
        msg = get_cmd_msg([0x01, 0x09], self.can_id)
        self.write_cmd(msg, "enable_motors")


    @function_prints
    def cmd_reset_position(self):
        """Needs to be sent 2 times within 20ms at start."""
        msg = get_cmd_msg ([0x01, 0x08, 0x0, 0x0], self.can_id)
        self.write_cmd(msg, "reset_position")
    
    
    @function_prints
    def cmd_reference(self):
        msg = get_cmd_msg([0x01, 0x0B], self.can_id)
        self.write_cmd(msg, "reference")


    @function_prints
    def cmd_disable_motor(self):
        msg = get_cmd_msg([0x01, 0x0A], self.can_id)
        self.write_cmd(msg, "disable_motors")


    @function_prints
    def cmd_allign_rotor(self):
        msg = get_cmd_msg([0x01, 0x0C], self.can_id)
        self.write_cmd(msg, "align_rotor")

    
    @function_prints
    def cmd_velocity_mode(self, velo=10):
        """Command for Velocity mode.
        Params:
        pcan: PCANBasic instance
        channel: Current PCANChannel
        velo: Velocity transmission-sided in [°/sec]"""
        
        # if abs(velo) > 36:
        #     raise TypeError("Parameter velo should not be greater than 36°/sec!")

        rpm = velo * 50/6 # w = 360°/6 * n[1/min] with [w] = °/sec; RPM_motor =  50* RPM_Gear
        velo_bytes = int_to_bytes(rpm, 2, True)

        
        msg = get_cmd_msg([0x25, *velo_bytes], self.can_id)
        self.write_cmd(msg, "velocity_mode")


    @function_prints
    def cmd_position_mode(self, to_tics:int, time_stamp:int):
        """Position mode with position in tics to move to.
        Params:
        - to_tics: Setpoint in delta tics.
        """
        if type(to_tics)  != int:
            raise ValueError("Tics need to be integer values.")
        
        tics_32_bits = int_to_bytes(to_tics, num_bytes=4, signed=True)
        msg = get_cmd_msg([0x14,0x0,*tics_32_bits, time_stamp, 0x0], self.can_id)    
        self.write_cmd(msg, "position_mode")

    
    @function_prints
    def timestamp_str(self, timestamp):
        return f"Timestamps Milliseconds: {timestamp.millis} // Milliseconds (overflow): {timestamp.millis_overflow} // Microseconds: {timestamp.micros}"

    @function_prints
    def status_str(self, status):
        return f"Current Status: {PCAN_DICT_STATUS.get(status)}"

   
    

if __name__ == "__main__":

    controller = RebelAxisController()
    
