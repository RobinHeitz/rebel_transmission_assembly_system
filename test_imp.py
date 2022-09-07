from data_management.model import Assembly, AssemblyStep, Failure, Measurement, Transmission, TransmissionConfiguration
from gui.improvement_window import improvement_window

from data_management import data_controller
from hw_interface.motor_controller import RebelAxisController

import random

def main():
    session = data_controller.create_session()

    controller = RebelAxisController()
    controller.connect()

    t = session.query(Transmission).order_by(Transmission.id.desc()).first()

    failures = session.query(Failure).all()
    selected_fail = random.choice(failures)

    possible_improvements = selected_fail.improvements
    selected_imp = random.choice(possible_improvements)

    m = session.query(Measurement).order_by(Measurement.id.desc()).first()
    session.close()

    improvement_window(controller, t, selected_fail, selected_imp, m, AssemblyStep.step_1_no_flexring)


def transmission_available():
    session = data_controller.create_session()
    transmissions = session.query(Transmission).all()

    if len(transmissions) == 0:
        data_controller.create_transmission(TransmissionConfiguration.config_105_break)
        data_controller.create_measurement(assembly=session.query(Assembly).order_by(Assembly.id.desc()).first())


if __name__ == "__main__":
    
    transmission_available()
    main()