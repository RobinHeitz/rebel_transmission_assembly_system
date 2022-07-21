
from hw_interface.motor_controller import RebelAxisController
import time



def do_cycle():
    time.sleep(1/50)

c = RebelAxisController()
c.start_msg_listener_thread()

time.sleep(2)
print("Time to reset errors:")

c.cmd_reset_position()
do_cycle()
c.cmd_reset_position()
do_cycle()


c.cmd_reset_errors()
do_cycle()
c.cmd_reset_errors()
do_cycle()

c.cmd_enable_motor()
time.sleep(2)



try:
    while True:
        print(f"Motor is aligned? {c.motor_rotor_is_aligned} // Errs resettet? {c.motor_no_err} // Referenced? {c.motor_referenced} // Motor enabled? {c.motor_enabled}")
        ...
        do_cycle()
        c.cmd_velocity_mode()


except KeyboardInterrupt:

    c.cmd_disable_motor()