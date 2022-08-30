# %%

import sqlalchemy as db

from data_management.model import Failure, FailureInstance, Transmission, TransmissionConfiguration, AssemblyStep, Improvement, ImprovementInstance
from data_management.model import Measurement, Assembly, AssemblyStep, DataPoint

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


    model_classes = [Transmission, Assembly, Measurement, DataPoint, FailureInstance, ImprovementInstance ]

    objects_to_delete = [i for c in model_classes for i in session.query(c).all()]
    for i in objects_to_delete:
        session.delete(i)
    session.flush()

    t = Transmission()
    session.add(t)



    session.commit()



