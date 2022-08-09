import threading
from can.interfaces.pcan.basic import PCANBasic,PCAN_USBBUS1, PCAN_BAUD_500K, PCAN_ERROR_OK
import time

from hw_interface.definitions import MessageEnvironmentStatus, MessageMovementCommandReply, Exception_Movement_Command_Reply_Error, MovementPositionMode, MovementVelocityMode
from hw_interface.motor_controller import RebelAxisController




###########################################
# Using MotorController Class to move motor
###########################################


# def send_pos_cmd_thread(controller:RebelAxisController, velo=10):
    
#     """
#     output_velocity = frequency * delta_tics / GearScale
#     <=> delta_Tics = output_velocity * GearScale / frequency
#     """
#     frequency_hz = 20
#     err_reset_counter = 0

#     current_tics = controller.tics_current

#     currentThread = threading.current_thread()


#     tics_setpoint = 0
#     timestamp = 0


#     tics_increment = 100

#     controller.cmd_reset_position()
#     time.sleep(0.02)
#     controller.cmd_reset_position()

#     time.sleep(1)

#     while getattr(currentThread, "done", False) == False:

#         tics_setpoint = getattr(currentThread, 'tics_setpoint', 0)
        
#         if not controller.can_move():
#             if err_reset_counter >= 5:
#                 print("ERROR RESET 5 TIMES!")
#                 break
#             controller.cmd_reset_errors()
#             controller.cmd_enable_motor()
#             err_reset_counter += 1

#         timestamp = (timestamp + 1) % 256
        
#         current_tics = current_tics + tics_increment
        
#         print("Controller send pos cmd: Current Tics = ", current_tics, "controller current tics: ", controller.tics_current, "lag=", current_tics-controller.tics_current)
        
#         controller.cmd_position_mode(current_tics, timestamp)

#         time.sleep(1/frequency_hz)
#     controller.stop_movement()




if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Script so useful.')
    parser.add_argument("-v", "--verbose", action="store_true", help="increase verbosity of log file.")
    args = parser.parse_args()
    verbose = args.verbose

    c = RebelAxisController(verbose=verbose)
    c.start_msg_listener_thread()
    c.start_movement_thread()



    try:
        print("Waiting for start!")
        time.sleep(1)

        m = MovementPositionMode(150000)
        c.movement_queue.append(m)
        print("Added movement action to queue")


        while c.movement_queue[0].finished == False:
            print("..")
            time.sleep(5)
        
        print("Action finished!")
        c.movement_queue.pop(0)

        time.sleep(3)

        m = MovementPositionMode(0)
        c.movement_queue.append(m)
        print("Added movement action to queue")

        while c.movement_queue[0].finished == False:
            print("..")
            time.sleep(5)

    except KeyboardInterrupt:
        c.stop_movement()
