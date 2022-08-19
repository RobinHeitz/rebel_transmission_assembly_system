# %%
from sqlalchemy.orm.session import Session
import sqlalchemy as db

from datetime import datetime
from random import randint
import time


from data_management.model import Transmission, TransmissionConfiguration
from data_management.model import Measurement, Assembly, AssemblyStep, DataPoint


from sqlalchemy.orm import sessionmaker


def create_assembly_step(session:Session, transmission, assembly_step:AssemblyStep):
    assembly = Assembly(assembly_step = assembly_step, transmission = transmission)
    session.add(assembly)

    for m in range(2):
        ...
        # create 5 measurement objects
        measurement_ = Measurement(title=f"Assmebly: {assembly} No. {m}", assembly=assembly)
        session.add(measurement_)

        for i in range(5):
            point = DataPoint(
                current = randint(150,450), 
                timestamp = datetime.now().timestamp(), 
                measurement = measurement_, 
            )
            session.add(point)
            time.sleep(0.02)



def create_assemblies(session:Session, transmission:Transmission):
    assembly_steps = AssemblyStep.get_all_steps()

    for step in assembly_steps:
        create_assembly_step(session, transmission, step)

    
    






if __name__ == "__main__":
    engine = db.create_engine('sqlite:///rebel.sqlite')
    connection = engine.connect()
    metadata = db.MetaData()
    session = sessionmaker(bind = engine)()

    new_transmission = Transmission(
        transmission_configuration = TransmissionConfiguration.config_105_break_encoder,
    )

    session.add(new_transmission)
    create_assemblies(session, new_transmission)

    print("About to commit changes!")
    session.commit()

    
    # t = Transmission(
    #     transmission_configuration = TransmissionConfiguration.config_105_break_encoder,
    # )
    # session.add(t)

    # a = Assembly(assembly_step = AssemblyStep.step_1_no_flexring, transmission=t)
    # session.add(a)

    # session.commit








# session.add(new_transmission)
# session.commit()


    # author = db.Table('Author', metadata, autoload=True, autoload_with=engine)
    # print(author.columns.keys())


    # # Session = sessionmaker(bind = engine)
    # # session = Session()

    # book = db.Table('book', metadata, autoload=True, autoload_with=engine)
    # print(book.columns.keys())


# # %%

# assembly = Assembly(assembly_step = AssemblyStep.step_1_no_flexring, transmission = new_transmission)

# session.add(assembly)
# session.commit()

# # %%
# measurement = Measurement(title="Test", assembly = assembly)
# session.add(measurement)
# session.commit()


# # %%


# get_trans = db.Table("Transmission", metadata, autoload=True, autoload_with=engine)
# print(get_trans.columns.keys())
