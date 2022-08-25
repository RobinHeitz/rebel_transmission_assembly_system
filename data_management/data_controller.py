from multiprocessing.sharedctypes import Value
from sqlalchemy.orm.session import Session
from sqlalchemy.orm import sessionmaker, scoped_session
import sqlalchemy as db

from data_management.model import Transmission, TransmissionConfiguration
from data_management.model import Measurement, Assembly, AssemblyStep, DataPoint

from typing import List




engine = db.create_engine("sqlite:///rebel.sqlite", connect_args={'check_same_thread':False},)
connection = engine.connect()
metadata = db.MetaData()

# session = sessionmaker(bind = engine)()

current_transmission = None
current_assembly = None
current_measurement = None

current_assemblies = dict()

######################
#### helper functions
######################

def create_session(f):
    def wrap(*args, **kwargs):
        session_factory = sessionmaker(bind=engine)
        Session = scoped_session(session_factory)
        session = Session()
        
        return_val = f(session, *args, **kwargs)
        Session.remove()
        return return_val
    return wrap


@create_session
def get_current_measurement_instance(session:Session):
    return session.query(Measurement).order_by(Measurement.measurement_id.desc()).first()


def update_current_measurement_fields():
    m = get_current_measurement_instance()
    update_measurement_fields(m)

@create_session
def update_measurement_fields(session:Session, m:Measurement):

    datapoints_ = session.query(DataPoint).filter_by(measurement=m)
    
    current_values = [dp.current for dp in datapoints_]
    m.max_current = round(max(current_values),2)
    m.min_current = round(min(current_values),2)
    m.mean_current = round(sum(current_values) / len(current_values) ,2)
    session.commit()


##################
### Create objects
##################

@create_session
def get_or_create_transmission(session:Session, config:TransmissionConfiguration) -> Transmission:
    global current_transmission
    
    if current_transmission != None:
        return current_transmission
    
    if config == None:
        raise ValueError("Config shouldn't be None if Transmission gets created.")

    current_transmission = Transmission(transmission_configuration = config)
    session.add(current_transmission)
    session.commit()
    return current_transmission

@create_session
def get_or_create_assembly_for_assembly_step(session:Session, assembly_step:AssemblyStep, transmission:Transmission = None) -> Assembly:

    global current_assemblies

    if assembly_step in current_assemblies:
        return current_assemblies[assembly_step]
    
    if transmission == None:
        raise ValueError("Transmission shouldn't be None if Assembly gets created.")
    
    a = Assembly(assembly_step = assembly_step, transmission = transmission)
    session.add(a)
    session.commit()

    current_assemblies[assembly_step] = a
    return a


@create_session
def create_measurement(session:Session, assembly:Assembly) -> Measurement:
    global current_measurement
    current_measurement = Measurement(assembly = assembly)
    
    session.add(current_measurement)
    session.commit()

    return current_measurement


@create_session
def create_data_point(session:Session, current, timestamp, measurement:Measurement):
   
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




