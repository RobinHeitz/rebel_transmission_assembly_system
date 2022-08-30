from gui.improvement_window import improvement_window

from data_management import data_controller
from hw_interface.motor_controller import RebelAxisController

imp = data_controller.get_random_improvement_instance()
controller = RebelAxisController()


improvement_window(controller, imp)