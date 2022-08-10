import threading
from can.interfaces.pcan.basic import PCANBasic,PCAN_USBBUS1, PCAN_BAUD_500K, PCAN_ERROR_OK
import time

from hw_interface.definitions import MessageEnvironmentStatus, MessageMovementCommandReply, Exception_Movement_Command_Reply_Error, MovementPositionMode, MovementVelocityMode
from hw_interface.motor_controller import RebelAxisController

import random


###########################################
# Using MotorController Class to move motor
###########################################


def generate_random_action():
    pos = random.randint(-3712*50,3712*50)
    velo = random.randint(15,40)
    return MovementPositionMode(pos,velo)




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
        
        for i in range(5):
            m = generate_random_action()
            # m = MovementPositionMode(15000*i, 10, 1000)
            c.movement_queue.append(m)
        
        # Homing after work is done.
        c.movement_queue.append(
            MovementPositionMode(0,20)
        )
        
        print("Waiting for start!")
        time.sleep(1)


        while len(c.movement_queue) > 0:
            print("..")
            time.sleep(5)
        
        print("Action finished!")

    except KeyboardInterrupt:
        c.stop_movement()
