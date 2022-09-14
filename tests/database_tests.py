import unittest

from data_management import data_controller
from data_management.data_controller import create_database, create_session
from data_management.model import Assembly, AssemblyStep, Improvement, Failure, Transmission, Measurement, DataPoint, ImprovementInstance, FailureInstance, TransmissionConfiguration




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
        ...




    


