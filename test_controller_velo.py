from threading import Thread
import time

from hw_interface.definitions import MessageEnvironmentStatus, MessageMovementCommandReply, Exception_Movement_Command_Reply_Error
from hw_interface.motor_controller import RebelAxisController




###########################################
# Using MotorController Class to move motor
###########################################

if __name__ == "__main__":
    ...

    import argparse
    parser = argparse.ArgumentParser(description='Script so useful.')
    parser.add_argument("-v", "--verbose", action="store_true", help="increase verbosity of log file.")
    args = parser.parse_args()
    verbose = args.verbose


    c = RebelAxisController(verbose=verbose)
    c.start_msg_listener_thread()

    max_err_reset = 5
    err_reset_counter = 0
    
    try:
        ...
        time.sleep(1)
        print("START")

        c.cmd_reset_position()
        c.do_cycle()
        c.cmd_reset_position()
        c.do_cycle()

        print("Start moving now")




        #################
        # WORKIGN EXAMPLE
        #################
        while True:
            try:

                if c.motor_no_err == False:
                    raise Exception_Movement_Command_Reply_Error(c.movement_cmd_errors)

                c.cmd_velocity_mode(10)
                c.do_cycle()
            
            except Exception_Movement_Command_Reply_Error:
                if max_err_reset >= err_reset_counter:
                    ...
                    c.cmd_reset_errors()
                    c.do_cycle()
                    c.cmd_enable_motor()
                    c.do_cycle()
                    err_reset_counter += 1
                else:
                    c.stop_movement()
                    break



    except KeyboardInterrupt:
        c.stop_movement()
    