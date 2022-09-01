from sqlalchemy.orm.session import Session
from sqlalchemy.orm import sessionmaker, scoped_session
import sqlalchemy as db
from sqlalchemy.exc import InvalidRequestError, ResourceClosedError

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


def create_session() -> Session:
    factory = sessionmaker(bind=engine, expire_on_commit=True)
    session = scoped_session(factory)()
    return session

def catch_exceptions(f):
    
    def _log_e(f, e):
        logger.error(f"Exception occured while doing db operations: {f.__name__}.")
        logger.error(traceback.format_exc())

    
    def wrap(*args, **kwargs):
        try:
            logger.info(f"--- {f.__name__}() called")
           
            session_obj = create_session()
           
            return_val = f(session_obj, *args, **kwargs)
            # session_obj.close()
            return return_val

        except Exception as e:
            _log_e(f,e)
        
        finally:
            session_obj.close()

    return wrap



#####################
###  Transmission ###
#####################

@catch_exceptions
def create_transmission(session:Session, config:TransmissionConfiguration) -> Transmission:
    # session = get_session()
    if config == None:
        raise ValueError("Config shouldn't be None if Transmission gets created.")

    t = Transmission(transmission_configuration = config)
    session.add(t)

    for step in AssemblyStep:
        a = Assembly(transmission = t, assembly_step = step)
        session.add(a)

    session.commit()
    return t


@catch_exceptions
def get_current_transmission(session:Session, ):
    # session = get_session()
    t = session.query(Transmission).order_by(Transmission.id.desc()).first()
    logger.info(f"get_current_transmissio (): {t}")
    return t


################
### Assembly ###
################


@catch_exceptions
def get_assembly_from_current_transmission(session:Session, step:AssemblyStep) -> Assembly:
    """Returns assembly (filtered by param: Step) from current transmission."""
    # session = get_session()
    t = session.query(Transmission).order_by(Transmission.id.desc()).first()
    return session.query(Assembly).filter_by(transmission=t, assembly_step=step).first()


###################
### Measurement ###
###################

@catch_exceptions
def get_current_measurement_instance(session:Session, ) -> Measurement:
        # session = get_session()
    returnVal =  session.query(Measurement).order_by(Measurement.id.desc()).first()
    return returnVal
    
        

@catch_exceptions
def create_measurement(session:Session, assembly:Assembly) -> Measurement:
    """Creates a measurement-obj.
    Parameters:
    - assembly:Assembly -> Assembly-instance measurement gets attached to."""
    # session = get_session()
    new_measure = Measurement(assembly = assembly)
    
    session.add(new_measure)
    session.commit()
    return new_measure





@catch_exceptions
def update_current_measurement_fields(session:Session, ):
    # session = get_session()
    m = session.query(Measurement).order_by(Measurement.id.desc()).first()
    datapoints_ = session.query(DataPoint).filter_by(measurement=m)
    
    current_values = [dp.current for dp in datapoints_]
    m.max_current = round(max(current_values),2)
    m.min_current = round(min(current_values),2)
    m.mean_current = round(sum(current_values) / len(current_values) ,2)
    session.commit()

    # return m


@catch_exceptions
def get_plot_data_for_current_measurement(session:Session, )-> List[Tuple]:
    """Returns list of (timestamp, current) of current measurement for plotting."""
    # session = get_session()
    m = get_current_measurement_instance()

    datapoints = session.query(DataPoint).filter_by(measurement=m)
    return [(d.timestamp, d.current) for d in datapoints]


##################
### DataPoints ###
##################

@catch_exceptions
def create_data_point(session:Session, current, timestamp, measurement:Measurement):
    # session = get_session()
   
    dp = DataPoint(current = current, timestamp = timestamp, measurement = measurement)
    session.add(dp)
    session.commit()

    return dp


@catch_exceptions
def create_data_point_to_current_measurement(session:Session, current, timestamp):
    return create_data_point(current, timestamp, get_current_measurement_instance())



# def get_failures_list_for_assembly_step(step:AssemblyStep):
#     logger.info("get_failures_list_for_assembly_step()")
#     session = get_session()
#     failures = session.query(Failure).filter_by(assembly_step = step).all()
#     if failures == None:
#         return []
    # return failures

@catch_exceptions
def create_failure_instance(session:Session, failure:Failure):
    # session = get_session()
    f = FailureInstance(failure_id=failure.id, transmission = get_current_transmission())
    session.add(f)
    session.commit()
    return f


################
### FAILURES ###
################

@catch_exceptions
def delete_failure_instance(session:Session, fail_instance: FailureInstance):
    # session = get_session()
    session.delete(fail_instance)
    session.commit()



@catch_exceptions
def sorted_failures_by_incidents(session:Session, step:AssemblyStep):
    # session = get_session()
    
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

@catch_exceptions
def create_improvement_instance(session:Session, imp:Improvement):
    # session = get_session()
    i = ImprovementInstance(improvement_id=imp.id, transmission=get_current_transmission())
    session.add(i)
    session.commit()
    return i


@catch_exceptions
def get_improvements_for_failure(session:Session, fail:Failure) -> List[Improvement]:
    # session = get_session()
    failure = session.query(Failure).get(fail.id)

    if failure == None:
        return []
    
    improvements = failure.improvements
    return improvements

@catch_exceptions
def delete_improvement_instance(session:Session, imp_instance: ImprovementInstance):
    # session = get_session()
    session.delete(imp_instance)
    session.commit()



@catch_exceptions
def setup_improvement_start(session:Session, failure:Failure, improvement:Improvement, m:Measurement) -> Tuple[FailureInstance, ImprovementInstance]:
    """Setup all necessary objects for improvement!"""
    # session = get_session()
    t = get_current_transmission()

    failure_instance = FailureInstance(failure = failure, transmission=t, measurement=m)
    session.add(failure_instance)

    improvement_instance = ImprovementInstance(improvement = improvement, transmission = t, failure_instance=failure_instance)
    session.add(improvement_instance)
    session.commit()

    return failure_instance, improvement_instance

@catch_exceptions
def set_success_status(session:Session, imp_instance:ImprovementInstance, status:bool):
    # session = get_session()
    imp_instance.successful = status
    session.commit()
    return imp_instance

@catch_exceptions
def update_improvement_measurement_relation(session:Session, m:Measurement, imp_instance:ImprovementInstance):
    # session = get_session()
    imp_instance.measurement = m
    session.flush()