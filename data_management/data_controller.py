from sqlalchemy.orm.session import Session
from sqlalchemy.orm import sessionmaker, scoped_session
import sqlalchemy as db

from data_management.model import Failure, FailureType, Transmission, TransmissionConfiguration
from data_management.model import Measurement, Assembly, AssemblyStep, DataPoint

from typing import List, Tuple

engine = db.create_engine("sqlite:///rebel.sqlite", connect_args={'check_same_thread':False},)
connection = engine.connect()
metadata = db.MetaData()

current_transmission = None

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
def create_transmission(session:Session, config:TransmissionConfiguration) -> Transmission:
    if config == None:
        raise ValueError("Config shouldn't be None if Transmission gets created.")

    t = Transmission(transmission_configuration = config)
    session.add(t)

    for step in AssemblyStep:
        a = Assembly(transmission = t, assembly_step = step)
        session.add(a)

    session.commit()
    return t


def get_current_transmission(session:Session):
    return session.query(Transmission).order_by(Transmission.transmission_id.desc()).first()


@create_session
def get_assembly_from_current_transmission(session:Session, step:AssemblyStep) -> Assembly:
    """Returns assembly (filtered by param: Step) from current transmission."""
    t = session.query(Transmission).order_by(Transmission.transmission_id.desc()).first()
    return session.query(Assembly).filter_by(transmission=t, assembly_step=step).first()


@create_session
def get_failure_type_for_description_and_assembly_step(session:Session, description:str, assembly_step:AssemblyStep):
    query_result = session.query(FailureType).filter_by(description = description, assembly_step = assembly_step)
    if len(query_result.all()) > 1:
        raise Exception("This should never be greater 1!")
    return query_result.first()

@create_session
def create_failure(session:Session, failure_type:FailureType):

    transmission = get_current_transmission(session)

    print("TRANSMISSION = ", transmission, type(transmission))
    print("FailureType = ", failure_type, type(failure_type))

    f = Failure(failure_type = failure_type, transmission = transmission)
    session.add(f)

    session.commit()

@create_session
def create_measurement(session:Session, assembly:Assembly) -> Measurement:
    new_measure = Measurement(assembly = assembly)
    
    session.add(new_measure)
    session.commit()

    return new_measure


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
    """Returns list of (timestamp, current) of current measurement for plotting."""
    m = get_current_measurement_instance()

    datapoints = session.query(DataPoint).filter_by(measurement=m)
    return [(d.timestamp, d.current) for d in datapoints]



@create_session
def get_failure_types(session:Session, assembly_step:AssemblyStep) -> str:
    return session.query(FailureType).filter_by(assembly_step = assembly_step).all()




