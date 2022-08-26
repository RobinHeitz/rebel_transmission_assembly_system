# %%

import sqlalchemy as db

from data_management.model import Failure, IndicatorType, Transmission, TransmissionConfiguration, AssemblyStep
from data_management.model import Measurement, Assembly, AssemblyStep, DataPoint, Indicator, Failure

import random

engine, connection, metadata, session = None, None, None, None


def setup_session():
    global engine, connection, metadata, session

    engine = db.create_engine('sqlite:///rebel.sqlite')
    connection = engine.connect()
    metadata = db.MetaData()
    session = sessionmaker(bind = engine)()
    


from sqlalchemy.orm import sessionmaker

if __name__ == "__main__":

    setup_session()


    model_classes = [Transmission, Assembly, Measurement, DataPoint, Indicator, Failure]

    objects_to_delete = [i for c in model_classes for i in session.query(c).all()]
    for i in objects_to_delete:
        session.delete(i)
    
    session.flush()

    # Transmission

    indicators = [
        "Schleifen/ zyklisches Klacken", 
        "Bewegung des Motors mit Steuerung nicht möglich", 
        "Encoder-Error in Anzeige", 
        "Ruckeln bei Bewegung des Motors", 
        "Stromverlauf schwankt zu stark", 
        "Abtrieb (Magnetring)", 
        "Quietschen",
    ]



    t = Transmission(transmission_configuration = TransmissionConfiguration.config_105_break_encoder)

    session.add(t)

    for step in AssemblyStep:

        oc = Indicator(description = "Strom > Nennwert", assembly_step = step, indicator_type = IndicatorType.overcurrent)
        other_indicator = Indicator(description = random.choice(indicators), assembly_step = step, indicator_type = IndicatorType.not_measurable)
        
        # overcurrent = FailureType(description = f"Current to high for this assembly step {step.value}", assembly_step = step, failure_classification = FailureClassification.overcurrent)
        # vibrations = FailureType(description = f"To high vibrations: {step.value}", assembly_step = step)
        # squeaks = FailureType(description = f"Transmission is squeaking: {step.value}", assembly_step = step)
        
        session.add(oc)
        session.add(other_indicator)

    session.commit()



