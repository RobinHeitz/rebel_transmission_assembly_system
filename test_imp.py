from gui.improvement_window import improvement_window

from data_management import data_controller
from hw_interface.motor_controller import RebelAxisController

controller = RebelAxisController()

improvement = data_controller._get_random_improvement()


improvement_window(controller, improvement)