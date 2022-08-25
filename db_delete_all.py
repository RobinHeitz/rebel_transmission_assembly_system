# %%

import sqlalchemy as db

from data_management.model import Failure, Transmission, TransmissionConfiguration, AssemblyStep
from data_management.model import Measurement, Assembly, AssemblyStep, DataPoint, FailureType, FailureClassification

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


    model_classes = [Transmission, Assembly, Measurement, DataPoint, FailureType, Failure]

    objects_to_delete = [i for c in model_classes for i in session.query(c).all()]
    for i in objects_to_delete:
        session.delete(i)
    
    session.flush()


    for step in AssemblyStep:
        
        overcurrent = FailureType(description = f"Current to high for this assembly step {step.value}", assembly_step = step, failure_classification = FailureClassification.failure_type_overcurrent)
        vibrations = FailureType(description = f"To high vibrations: {step.value}", assembly_step = step)
        squeaks = FailureType(description = f"Transmission is squeaking: {step.value}", assembly_step = step)
        
        session.add(overcurrent)
        session.add(vibrations)
        session.add(squeaks)

    session.commit()



