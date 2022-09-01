from sqlalchemy.orm.session import Session
from sqlalchemy.orm import sessionmaker, scoped_session
import sqlalchemy as db

from data_management.model import Transmission, TransmissionConfiguration
from data_management.model import Measurement, Assembly, AssemblyStep, DataPoint
from data_management.model import Failure, FailureInstance, Improvement, ImprovementInstance, FailureType

import traceback
import threading
from typing import List, Tuple

# logger setup

from logs.setup_logger import setup_logger
logger = setup_logger("data_controller")


engine = db.create_engine("sqlite:///rebel.sqlite", connect_args={'check_same_thread':False},)
connection = engine.connect()
metadata = db.MetaData()

current_transmission = None


session = None
######################
#### helper functions
######################

def  get_session() -> Session:
    global session
    if session == None:
        factory = sessionmaker(bind=engine, expire_on_commit=False)
        session = scoped_session(factory)()

    return session

#####################
###  Transmission ###
#####################

# @create_session
def create_transmission(config:TransmissionConfiguration) -> Transmission:
    logger.info("create_transmission()")
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
    t = session.query(Transmission).order_by(Transmission.id.desc()).first()
    logger.info(f"get_current_transmissio (): {t}")
    return t


################
### Assembly ###
################


def get_assembly_from_current_transmission(step:AssemblyStep) -> Assembly:
    """Returns assembly (filtered by param: Step) from current transmission."""
    logger.info("get_assembly_from_current_transmission")
    session = get_session()
    t = session.query(Transmission).order_by(Transmission.id.desc()).first()
    return session.query(Assembly).filter_by(transmission=t, assembly_step=step).first()


###################
### Measurement ###
###################

def get_current_measurement_instance() -> Measurement:
    logger.info("get_current_measurement_instance")
    session = get_session()
    return session.query(Measurement).order_by(Measurement.id.desc()).first()


def create_measurement(assembly:Assembly) -> Measurement:
    """Creates a measurement-obj.
    Parameters:
    - assembly:Assembly -> Assembly-instance measurement gets attached to."""
    logger.info("create_measurement")
    session = get_session()
    new_measure = Measurement(assembly = assembly)
    
    session.add(new_measure)
    session.commit()
    return new_measure





def update_current_measurement_fields():
    logger.info("update_current_measurement_fields()")
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
    logger.info("get_plot_data_for_current_measurement()")
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
    logger.info("create_data_point()")
    session = get_session()
   
    dp = DataPoint(current = current, timestamp = timestamp, measurement = measurement)
    session.add(dp)
    session.commit()

    return dp


def create_data_point_to_current_measurement(current, timestamp):
    logger.info("create_data_point_to_current_measurement()")
    session = get_session()
    return create_data_point(current, timestamp, get_current_measurement_instance())



# def get_failures_list_for_assembly_step(step:AssemblyStep):
#     logger.info("get_failures_list_for_assembly_step()")
#     session = get_session()
#     failures = session.query(Failure).filter_by(assembly_step = step).all()
#     if failures == None:
#         return []
    return failures

def create_failure_instance(failure:Failure):
    logger.info("create_failure_instance()")
    session = get_session()
    f = FailureInstance(failure_id=failure.id, transmission = get_current_transmission())
    session.add(f)
    session.commit()
    return f


################
### FAILURES ###
################

def delete_failure_instance(fail_instance: FailureInstance):
    logger.info("delete_failure_instance()")
    session = get_session()
    session.delete(fail_instance)
    session.commit()



def sorted_failures_by_incidents(step:AssemblyStep):
    logger.info("rank_failures(): Should return a list of failures with ranked positions by probability of occurrence.")
    session = get_session()
    
    # total_failure_occurences = session.query(FailureInstance).filter_by(assembly_step = step).count() 
    
    logger.info("##"*5)
    logger.info("Testing sorting of failures by number of incidents")

    failures_without_oc: List[Failure] = session.query(Failure).filter(Failure.failure_type != FailureType.overcurrent, Failure.assembly_step == step).all()
    failures_sorted = sorted(failures_without_oc, key=lambda f: len(f.failure_instances), reverse=True)

    logger.info(f"Before: {failures_without_oc}")
    logger.info(f"After: {failures_sorted}")

    return failures_sorted



####################
### IMPROVEMENTS ###
####################

def create_improvement_instance(imp:Improvement):
    logger.info("create_improvement_instance()")
    session = get_session()
    i = ImprovementInstance(improvement_id=imp.id, transmission=get_current_transmission())
    session.add(i)
    session.commit()
    return i


def get_improvements_for_failure(fail:Failure) -> List[Improvement]:
    logger.info("get_improvements_for_failure()")
    session = get_session()
    failure = session.query(Failure).get(fail.id)

    if failure == None:
        return []
    
    improvements = failure.improvements
    return improvements

def delete_improvement_instance(imp_instance: ImprovementInstance):
    logger.info("delete_improvement_instance()")
    session = get_session()
    session.delete(imp_instance)
    session.commit()



def setup_improvement_start(failure:Failure, improvement:Improvement, m:Measurement) -> Tuple[FailureInstance, ImprovementInstance]:
    """Setup all necessary objects for improvement!"""
    logger.info("setup_improvement_start()")
    session = get_session()
    t = get_current_transmission()

    failure_instance = FailureInstance(failure = failure, transmission=t, measurement=m)
    session.add(failure_instance)

    improvement_instance = ImprovementInstance(improvement = improvement, transmission = t, failure_instance=failure_instance)
    session.add(improvement_instance)
    session.commit()

    return failure_instance, improvement_instance

def set_success_status(imp_instance:ImprovementInstance, status:bool):
    logger.info(f"set_success_status() | improvement-instance to set: {imp_instance} / new status: {status}")
    session = get_session()
    imp_instance.successful = status
    session.commit()
    return imp_instance

def update_improvement_measurement_relation(m:Measurement, imp_instance:ImprovementInstance):
    logger.info(f"update_improvement_measurement_relation()")
    session = get_session()
    imp_instance.measurement = m
    session.flush()