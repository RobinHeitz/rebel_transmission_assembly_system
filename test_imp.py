from data_management.model import Failure, Measurement
from gui.improvement_window import improvement_window

from data_management import data_controller
from hw_interface.motor_controller import RebelAxisController

import random

def main():
    controller = RebelAxisController()

    session = data_controller.create_session()

    failures = session.query(Failure).all()
    selected_fail = random.choice(failures)

    possible_improvements = selected_fail.improvements

    selected_imp = random.choice(possible_improvements)



    # selected_fail = session.query(Failure).first()
    # selected_imp = selected_fail.improvements[0]

    m = session.query(Measurement).order_by(Measurement.id.desc()).first()

    print("+++"*5)
    print(selected_fail, selected_imp)

    improvement_window(controller, selected_fail, selected_imp, m)


if __name__ == "__main__":
    main()