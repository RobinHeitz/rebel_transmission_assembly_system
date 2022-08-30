from cmath import exp
from sqlalchemy.orm.session import Session
from sqlalchemy.orm import sessionmaker, scoped_session
import sqlalchemy as db

from data_management.model import Transmission, TransmissionConfiguration
from data_management.model import Measurement, Assembly, AssemblyStep, DataPoint
from data_management.model import Failure, FailureInstance, Improvement, ImprovementInstance

import traceback
import threading

from typing import List, Tuple

engine = db.create_engine("sqlite:///rebel.sqlite", connect_args={'check_same_thread':False},)
connection = engine.connect()
metadata = db.MetaData()

current_transmission = None

current_assemblies = dict()

# testing:

# factory = sessionmaker(bind=engine, expire_on_commit=False)
# session = scoped_session(factory)()

sessions = {}

######################
#### helper functions
######################

def  get_session() -> Session:
    ...
    thread_id = threading.get_ident()

    try:
        session = sessions[thread_id]
        return session
    except KeyError:
        factory = sessionmaker(bind=engine, expire_on_commit=False)
        session = scoped_session(factory)()

        sessions[thread_id] = session
        return session





def create_session(f):
    def wrap(*args, **kwargs):
        session_factory = sessionmaker(bind=engine,expire_on_commit=False)
        Session = scoped_session(session_factory)
        session = Session()
        
        return_val = f(session, *args, **kwargs)
        Session.remove()
        return return_val
    return wrap



#####################
###  Transmission ###
#####################

# @create_session
def create_transmission(config:TransmissionConfiguration) -> Transmission:
    session = get_session()
    if config == None:
        raise ValueError("Config shouldn't be None if Transmission gets created.")

    t = Transmission(transmission_configuration = config)
    session.add(t)

    for step in AssemblyStep:
        a = Assembly(transmission = t, assembly_step = step)
        session.add(a)

    session.commit()
    return t


def get_current_transmission():
    session = get_session()
    return session.query(Transmission).order_by(Transmission.id.desc()).first()


################
### Assembly ###
################


def get_assembly_from_current_transmission(step:AssemblyStep) -> Assembly:
    """Returns assembly (filtered by param: Step) from current transmission."""
    session = get_session()
    t = session.query(Transmission).order_by(Transmission.id.desc()).first()
    return session.query(Assembly).filter_by(transmission=t, assembly_step=step).first()


###################
### Measurement ###
###################

def get_current_measurement_instance() -> Measurement:
    session = get_session()
    return session.query(Measurement).order_by(Measurement.id.desc()).first()


def create_measurement(assembly:Assembly) -> Measurement:
    """Creates a measurement-obj.
    Parameters:
    - assembly:Assembly -> Assembly-instance measurement gets attached to."""
    session = get_session()
    new_measure = Measurement(assembly = assembly)
    
    session.add(new_measure)
    session.commit()
    return new_measure





def update_current_measurement_fields():
    session = get_session()
    m = session.query(Measurement).order_by(Measurement.id.desc()).first()
    datapoints_ = session.query(DataPoint).filter_by(measurement=m)
    
    current_values = [dp.current for dp in datapoints_]
    m.max_current = round(max(current_values),2)
    m.min_current = round(min(current_values),2)
    m.mean_current = round(sum(current_values) / len(current_values) ,2)
    session.commit()


def get_plot_data_for_current_measurement()-> List[Tuple]:
    """Returns list of (timestamp, current) of current measurement for plotting."""
    session = get_session()
    try:
        
        m = get_current_measurement_instance()

        datapoints = session.query(DataPoint).filter_by(measurement=m)
        return [(d.timestamp, d.current) for d in datapoints]
    except Exception as e:
        print(traceback.format_exc(e))


##################
### DataPoints ###
##################


def create_data_point(current, timestamp, measurement:Measurement):
    session = get_session()
   
    dp = DataPoint(current = current, timestamp = timestamp, measurement = measurement)
    session.add(dp)
    session.commit()

    return dp


def create_data_point_to_current_measurement(current, timestamp):
    session = get_session()
    return create_data_point(current, timestamp, get_current_measurement_instance())




#################
### Indicator ###
#################

# @create_session
# def get_indicator_for_description_and_assembly_step(session:Session, description:str, assembly_step:AssemblyStep):
#     query_result = session.query(Indicator).filter_by(description = description, assembly_step = assembly_step)
#     if len(query_result.all()) > 1:
#         raise Exception("This should never be greater 1!")
#     return query_result.first()



# @create_session
# def get_indicators_for_assembly_step(session:Session, assembly_step:AssemblyStep):
#     return  session.query(Indicator).filter_by(assembly_step = assembly_step).all()

# @create_session
# def get_indicators_for_assembly_step_and_IndicatorType(session:Session, assembly_step:AssemblyStep, indicator_type:IndicatorType):
#     return session.query(Indicator).filter_by(assembly_step = assembly_step, indicator_type = indicator_type).all()




###############
### Failure ###
###############

# @create_session
# def get_failure_for_description_and_assembly_step(session:Session, description:str, assembly_step:AssemblyStep):
#     query_result = session.query(Failure).filter_by(description = description, assembly_step = assembly_step)
#     if len(query_result.all()) > 1:
#         raise Exception("This should never be greater 1!")
#     return query_result.first()



# @create_session
# def create_failure(session:Session, assembly_step:AssemblyStep) -> Failure:
#     ...

#     f = Failure()


# @create_session
# def get_failures_list_from_indicator(session:Session, indicator:Indicator):
#     indicator = session.query(Indicator).get(indicator.id)

#     if indicator == None:
#         return []
#     failures = indicator.failures
#     return failures

def get_failures_list_for_assembly_step(step:AssemblyStep):
    session = get_session()
    failures = session.query(Failure).filter_by(assembly_step = step).all()
    if failures == None:
        return []
    return failures

def create_failure_instance(failure:Failure):
    session = get_session()
    f = FailureInstance(failure_id=failure.id, transmission = get_current_transmission())
    session.add(f)
    session.commit()
    return f


####################
### IMPROVEMENTS ###
####################

def create_improvement_instance(imp:Improvement):
    session = get_session()
    i = ImprovementInstance(improvement_id=imp.id, transmission=get_current_transmission())
    session.add(i)
    session.commit()
    return i


def get_improvements_for_failure(fail:Failure) -> List[Improvement]:
    session = get_session()
    failure = session.query(Failure).get(fail.id)

    if failure == None:
        return []
    
    improvements = failure.improvements
    return improvements

def delete_improvement_instance(imp_instance):
    session = get_session()

    # imp = session.query(ImprovementInstance).get(imp_id)
    session.delete(imp_instance)
    session.commit()


def _get_random_improvement():
    session = get_session()
    return session.query(Improvement).first()


def setup_improvement_start(failure:Failure, improvement:Improvement) -> Tuple[FailureInstance, ImprovementInstance]:
    """Setup all necessary objects for improvement!"""
    session = get_session()
    t = get_current_transmission()

    failure_instance = FailureInstance(failure = failure, transmission=t)
    session.add(failure_instance)

    improvement_instance = ImprovementInstance(improvement = improvement, transmission = t)
    session.add(improvement_instance)
    session.commit()

    return failure_instance, improvement_instance
