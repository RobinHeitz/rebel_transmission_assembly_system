# %%

import sqlalchemy as db

from data_management.model import Failure, Transmission, TransmissionConfiguration, AssemblyStep
from data_management.model import Measurement, Assembly, AssemblyStep, DataPoint, FailureType


from sqlalchemy.orm import sessionmaker

if __name__ == "__main__":
    engine = db.create_engine('sqlite:///rebel.sqlite')
    connection = engine.connect()
    metadata = db.MetaData()
    session = sessionmaker(bind = engine)()

    model_classes = [Transmission, Assembly, Measurement, DataPoint, FailureType, Failure]

    objects_to_delete = [i for c in model_classes for i in session.query(c).all()]
    for i in objects_to_delete:
        session.delete(i)
    
    session.flush()


    for step in AssemblyStep:
        
        overcurrent = FailureType(description = f"Current to high for this assembly step! {step.value}", assembly_step = step)
        another_failure_type = FailureType(description = f"This is a failure, special to this assembly step: {step.value}", assembly_step = step)
        
        session.add(overcurrent)
        session.add(another_failure_type)

    session.commit()



