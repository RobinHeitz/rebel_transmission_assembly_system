from threading import Thread
from can.interfaces.pcan.basic import PCANBasic,PCAN_USBBUS1, PCAN_BAUD_500K, PCAN_ERROR_OK
import time

from hw_interface.definitions import MessageEnvironmentStatus, MessageMovementCommandReply, Exception_Movement_Command_Reply_Error
from hw_interface.motor_controller import RebelAxisController




###########################################
# Using MotorController Class to move motor
###########################################


if __name__ == "__main__":
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

        print("Start Rotor allignment")
        c.cmd_allign_rotor()
        c.cmd_allign_rotor()

        time.sleep(6)

        print("START Resetting")
        c.cmd_reset_position()
        c.do_cycle()
        c.cmd_reset_position()
        c.do_cycle()


        print("Start moving now")


        # delta_tics = 300

        #################
        # WORKIGN EXAMPLE
        #################


        if c.motor_no_err == False:
            c.cmd_reset_errors()
            c.do_cycle()
            c.cmd_enable_motor()
            c.do_cycle()

        c.move_position_mode2(target_pos=90)
        

    except KeyboardInterrupt:
        c.stop_movement()
    