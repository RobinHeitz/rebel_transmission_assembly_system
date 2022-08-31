from data_management.model import Failure, Measurement
from gui.improvement_window import improvement_window

from data_management import data_controller
from hw_interface.motor_controller import RebelAxisController


def main():
    controller = RebelAxisController()

    session = data_controller.get_session()

    selected_fail = session.query(Failure).first()
    selected_imp = selected_fail.improvements[0]

    m = session.query(Measurement).order_by(Measurement.id.desc()).first()

    print("+++"*5)
    print(selected_fail, selected_imp)

    improvement_window(controller, selected_fail, selected_imp, m)


if __name__ == "__main__":
    main()