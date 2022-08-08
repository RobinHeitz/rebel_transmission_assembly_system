from threading import Thread
import time

from hw_interface.definitions import MessageEnvironmentStatus, MessageMovementCommandReply, Exception_Movement_Command_Reply_Error
from hw_interface.motor_controller import RebelAxisController


###########################################
# Using MotorController Class to move motor
###########################################


if __name__ == "__main__":
    ...
    c = RebelAxisController()
    c.start_msg_listener_thread()

    max_err_reset = 5
    err_reset_counter = 0


    delta_tics = 100
    
    
    try:
        ...
        time.sleep(1)
        print("START Alignment")
        # c.cmd_allign_rotor()
        # c.cmd_allign_rotor()

        time.sleep(6)
        print("END ALLIGNMENT")

        c.cmd_reset_position()
        c.do_cycle()
        c.cmd_reset_position()
        c.do_cycle()

        print("Start moving now")


        time_stamp = 0

        #################
        # WORKIGN EXAMPLE
        #################
        while True:
            time_stamp = (time_stamp + 1) % 256
            c.tics_setpoint = c.tics_current + delta_tics
            try:

                if c.motor_no_err == False:
                    raise Exception_Movement_Command_Reply_Error(c.movement_cmd_errors)

                c.cmd_position_mode(c.tics_setpoint, time_stamp)
                # c.do_cycle()
                time.sleep(1/20)

            
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
    