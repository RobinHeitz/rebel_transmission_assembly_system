from data_management.model import Failure, Measurement
from gui.improvement_window import improvement_window

from data_management import data_controller
from hw_interface.motor_controller import RebelAxisController

import random

def main():
    session = data_controller.create_session()

    controller = RebelAxisController()

    failures = session.query(Failure).all()
    selected_fail = random.choice(failures)

    possible_improvements = selected_fail.improvements
    selected_imp = random.choice(possible_improvements)

    m = session.query(Measurement).order_by(Measurement.id.desc()).first()
    session.close()

    improvement_window(controller, selected_fail, selected_imp, m)


if __name__ == "__main__":
    main()