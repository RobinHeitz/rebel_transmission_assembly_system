from sqlalchemy.orm.session import Session
import sqlalchemy as db

from datetime import datetime
from random import randint
import time


from data_management.model import Transmission, TransmissionConfiguration
from data_management.model import Measurement, Assembly, AssemblyStep, DataPoint


from sqlalchemy.orm import sessionmaker

from typing import List

from ..hw_interface.definitions import MessageMovementCommandReply

engine = db.create_engine('sqlite:///rebel.sqlite')
connection = engine.connect()
metadata = db.MetaData()
session = sessionmaker(bind = engine)()



def main():
    ...

# def sample_data(samples:List[MessageMovementCommandReply]):
#     """Samples data from a list of MessageMovementCommandReply - objects.
#     Returns 3-tuple with current mean value, mid pos and mid millis (time stamp).
    
#     Params: 
#     - samples: List[MessageMovementCommandReply]"""
#     current_mean = sum([i.current for i in samples]) / len(samples)

#     if len(samples) % 2 == 0:
#         #even number of elements
#         lower_index = int( len(samples) / 2 -1 )
#         item_lower, item_upper = samples[lower_index: lower_index + 2]

#         pos = (item_lower.pos + item_upper.pos) / 2
#         millis = (item_lower.millis + item_upper.millis) / 2
#     else:
#         #uneven
#         index = int(len(samples) / 2)
#         pos, millis = samples[index].pos, samples[index].millis

#     return current_mean, pos, millis



# def main():
#     ...
#     new_transmission = Transmission(
#         transmission_configuration = TransmissionConfiguration.config_105_break_encoder,
#     )

#     session.add(new_transmission)
#     create_assemblies(session, new_transmission)

#     print("About to commit changes!")
#     session.commit()


# def create_assembly_step(session:Session, transmission, assembly_step:AssemblyStep):
#     assembly = Assembly(assembly_step = assembly_step, transmission = transmission)
#     session.add(assembly)

#     for m in range(2):
#         ...
#         # create 5 measurement objects
#         measurement_ = Measurement(title=f"Assmebly: {assembly} No. {m}", assembly=assembly)
#         session.add(measurement_)

#         for i in range(5):
#             point = DataPoint(
#                 current = randint(150,450), 
#                 timestamp = datetime.now().timestamp(), 
#                 measurement = measurement_, 
#             )
#             session.add(point)
#             time.sleep(0.02)



# def create_assemblies(session:Session, transmission:Transmission):
#     for step in AssemblyStep.get_all_steps():
#         create_assembly_step(session, transmission, step)





if __name__ == "__main__":
    main()