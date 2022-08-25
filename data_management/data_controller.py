from multiprocessing.sharedctypes import Value
from sqlalchemy.orm.session import Session
from sqlalchemy.orm import sessionmaker, scoped_session
import sqlalchemy as db

from data_management.model import Transmission, TransmissionConfiguration
from data_management.model import Measurement, Assembly, AssemblyStep, DataPoint

from typing import List, Tuple




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
def get_current_measurement_instance(session:Session) -> Measurement:
    return session.query(Measurement).order_by(Measurement.measurement_id.desc()).first()


@create_session
def update_current_measurement_fields(session:Session):
    m = session.query(Measurement).order_by(Measurement.measurement_id.desc()).first()
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



@create_session
def get_plot_data_for_current_measurement(session:Session)-> List[Tuple]:
    m = get_current_measurement_instance()

    datapoints = session.query(DataPoint).filter_by(measurement=m)
    return [(d.timestamp, d.current) for d in datapoints]
