from gui.improvement_window import improvement_window

from data_management import data_controller

imp = data_controller.get_random_improvement_instance()


improvement_window(imp)