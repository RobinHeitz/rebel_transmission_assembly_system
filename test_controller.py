
from hw_interface.motor_controller import RebelAxisController

c = RebelAxisController(0x10)
c.start_msg_listener_thread()

while True:
    ...
