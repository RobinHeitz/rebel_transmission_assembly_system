# %%

import sqlalchemy as db

from data_management.model import Transmission, TransmissionConfiguration
from data_management.model import Measurement, Assembly, AssemblyStep, DataPoint


from sqlalchemy.orm import sessionmaker

if __name__ == "__main__":
    engine = db.create_engine('sqlite:///rebel.sqlite')
    connection = engine.connect()
    metadata = db.MetaData()
    session = sessionmaker(bind = engine)()

    model_classes = [Transmission, Assembly, Measurement, DataPoint]

    objects_to_delete = [i for c in model_classes for i in session.query(c).all()]
    for i in objects_to_delete:
        session.delete(i)
    
    session.flush()
    session.commit()

