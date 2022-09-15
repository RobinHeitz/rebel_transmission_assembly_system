import unittest

from data_management import data_controller
from data_management.data_controller import create_database, create_session
from data_management.model import Assembly, AssemblyStep, FailureType, Improvement, Failure, Transmission, Measurement, DataPoint, ImprovementInstance, FailureInstance, TransmissionConfiguration




class TestClass(unittest.TestCase):

    def setUp(self) -> None:
        self.session = create_session()
    
    def tearDown(self) -> None:
        self.session.close()

    def test_transmission_creation(self):
        config = TransmissionConfiguration.config_105_break_encoder

        data_controller.create_transmission(config=config)
        transmission_counter = self.session.query(Transmission).count()
        self.assertGreaterEqual(transmission_counter, 1)


        steps = [s for s in AssemblyStep]
        numb_steps = len(steps)

        assembly_counter = self.session.query(Assembly).count()
        self.assertEqual(numb_steps * transmission_counter, assembly_counter)

    

    def test_get_failure_overcurrent(self):
        for s in AssemblyStep:
            f = data_controller.get_failure_overcurrent(step=s)
            self.assertIsNotNone(f)
            self.assertEqual(type(f), Failure)

    def test_get_failure_not_moving_OC(self):
        for s in AssemblyStep:
            f = data_controller.get_failure_not_moving_OC(step=s)
            self.assertIsNotNone(f)
            self.assertEqual(type(f), Failure)

    
    def test_get_improvements_for_failure(self):
        """Checks whether the correct number of improvements gets querried."""

        compare_data = {
            AssemblyStep.step_1_no_flexring: 5, 
            AssemblyStep.step_2_with_flexring: 3, 
            AssemblyStep.step_3_gearoutput_not_screwed: 3, 
        }

        for step in AssemblyStep:

            f_not_moving_OC = data_controller.get_failure_not_moving_OC(step)
            improvements = data_controller.get_improvements_for_failure(f_not_moving_OC, step)

            self.assertEqual(len(improvements), compare_data[step])

    

    def test_failure_sorting(self):
        ...

        with data_controller.session_context() as session:

            for s in AssemblyStep:

                failures_not_measureable = session.query(Failure).filter_by(assembly_step = s, failure_type = FailureType.not_measurable, is_verified = True).all()
                
                for i in range(len(failures_not_measureable)):
                    f = failures_not_measureable[i]

                    for j in range(i):
                        instance = FailureInstance(failure = f, assembly_step = s, failure_type = FailureType.not_measurable)
                        session.add(instance)
                
                session.commit()
                failures_sorted = data_controller.sorted_failures_by_incidents(s)
                self.assertEqual(failures_sorted, failures_not_measureable)

    
# %%

from ..data_management import data_controller

def test_improvement_sorting():

    with data_controller.session_context() as session:

        step = AssemblyStep.step_1_no_flexring
        failure = session.query(Failure).filter_by(assembly_step = step, failure_type = FailureType.not_measurable).first()

        imp = failure.improvements[0]



test_improvement_sorting()




        



    


