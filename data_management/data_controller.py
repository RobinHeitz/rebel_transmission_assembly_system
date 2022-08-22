from sqlalchemy.orm.session import Session
import sqlalchemy as db

from datetime import datetime
from random import randint
import time


from data_management.model import Transmission, TransmissionConfiguration
from data_management.model import Measurement, Assembly, AssemblyStep, DataPoint


from sqlalchemy.orm import sessionmaker

from typing import List


engine = db.create_engine('sqlite:///rebel.sqlite')
connection = engine.connect()
metadata = db.MetaData()
session = sessionmaker(bind = engine)()

current_transmission = None
current_assembly = None
current_measurement = None



def get_current_transmission_instance():
    return current_transmission

def get_current_assembly_instance():
    return current_assembly

def get_current_measurement_instance():
    return current_measurement


def create_transmission(config:TransmissionConfiguration):
    new_transmission = Transmission(transmission_configuration = config)
    session.add(new_transmission)
    session.commit()

    global current_transmission
    current_transmission = new_transmission
    return current_transmission


def create_assembly(transmission:Transmission, assembly_step: AssemblyStep):
    a = Assembly(assembly_step = assembly_step, transmission = transmission)
    session.add(a)
    session.commit()
    
    global current_assembly
    current_assembly = a
    return current_assembly


def create_measurement_to_current_assembly():
    return create_measurement(get_current_assembly_instance())


def create_measurement(assembly:Assembly):
    m = Measurement(assembly = assembly)
    session.add(m)
    session.commit()

    global current_measurement
    current_measurement = m
    return current_measurement

def create_data_point(current, timestamp, measurement:Measurement):
    dp = DataPoint(current = current, timestamp = timestamp, measurement = measurement)
    session.add(dp)
    session.commit()

    return dp



def create_data_point_to_current_measurement(current, timestamp):
    return create_data_point(current, timestamp, get_current_measurement_instance())




# def create_assemblies(transmission:Transmission):
#     for type_ in AssemblyStep:
#         assembly = Assembly()
        
#         assembly.assembly_type = AssemblyStep.step_1_no_flexring
#         assembly.transmission = transmission


#         session.add(assembly)
#     session.commit()

    

# def create_assembly(assembly_step: AssemblyStep, transmission:Transmission):
#     global current_assembly
#     current_assembly = Assembly(assembly_step, transmission)
#     session.add(current_assembly)


# def create_measurement(assembly_step: AssemblyStep):
#     global current_assembly, current_measurement
#     if current_assembly == None:
#         # create_assembly(assembly_step, get_current_transmission_instance())

#     # current_measurement = Measurement(
#     #     "Title 1 - Step 1",
#     #     # assembly = get_current_assembly_instance(),

#     # )
#     # session.add(current_measurement)
#     # session.commit()




# def create_data_point(current, timestamp):

#     dp = DataPoint(
#         current = current,
#         timestamp = timestamp,
#         # measurement = get_current_measurement_instance(),
#     )

#     session.add(dp)
#     session.commit()


# def create_data_points():
#     ...



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




