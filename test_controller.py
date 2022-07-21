
from hw_interface.motor_controller import RebelAxisController
import time



def do_cycle():
    time.sleep(1/50)

c = RebelAxisController()
c.start_msg_listener_thread()



try:

    if c.motor_enabled == False or c.motor_no_err == False:
        c.cmd_reset_errors()
        do_cycle()
        c.cmd_enable_motor()

    while True:
        do_cycle()
        c.cmd_velocity_mode()


except KeyboardInterrupt:

    c.cmd_disable_motor()