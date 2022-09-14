import unittest

from data_management.data_controller import create_session
from data_management.model import Improvement, Failure, Transmission, Measurement, DataPoint, ImprovementInstance, FailureInstance

class TestClass(unittest.TestCase):

    def setUp(self) -> None:
        self.session = create_session()
    
    def tearDown(self) -> None:
        self.session.close()



    def test_one(self):
        ...
        self.assertEqual('foo'.upper(), 'FOO')
