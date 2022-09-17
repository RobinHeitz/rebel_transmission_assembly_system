from sqlalchemy.orm.session import Session
from sqlalchemy.orm import sessionmaker, scoped_session
import sqlalchemy as db
from sqlalchemy.exc import InvalidRequestError, ResourceClosedError

from data_management.model import Transmission, TransmissionConfiguration
from data_management.model import Measurement, Assembly, AssemblyStep, DataPoint
from data_management.model import Failure, FailureInstance, Improvement, ImprovementInstance, FailureType

from contextlib import contextmanager

import traceback
import threading
from typing import List, Tuple, Set

# logger setup

from logs.setup_logger import setup_logger
logger = setup_logger("data_controller")


# engine = db.create_engine("sqlite:///rebel.sqlite", connect_args={'check_same_thread':False},)
# connection = engine.connect()
# metadata = db.MetaData()

current_transmission = None


# session = None
def create_database(db_name = "rebel.sqlite"):
    engine_str = f"sqlite:///{db_name}"
    engine = db.create_engine(engine_str, connect_args={'check_same_thread':False},)
    connection = engine.connect()
    # metadata = db.MetaData()
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    return scoped_session(factory)

def create_session() -> Session:
    return SessionCreate()

SessionCreate = create_database()



#Alternative: Using context-manager
@contextmanager
def session_context():
    session = create_session()
    try:
        yield session
    finally:
      session.close()


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
    # logger.info(f"get_current_transmissio (): {t}")
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




################
### FAILURES ###
################

@catch_exceptions
def create_failure_instance(session:Session, failure:Failure):
    # session = get_session()
    f = FailureInstance(failure_id=failure.id, transmission = get_current_transmission())
    session.add(f)
    session.commit()
    return f

@catch_exceptions
def delete_failure_instance(session:Session, fail_instance: FailureInstance):
    # session = get_session()
    session.delete(fail_instance)
    session.commit()


@catch_exceptions
def get_failure_overcurrent(session:Session, step: AssemblyStep):
    failures = session.query(Failure).filter_by(assembly_step = step, failure_type = FailureType.overcurrent, is_verified = True).all()
    if len(failures) != 1: raise Exception("DataStruture is corrupt! There should be only 1 instance of failure for a given AssemblyStep with FailureType overcurrent.")
    return failures[0]

@catch_exceptions
def get_failure_not_moving_OC(session:Session, step: AssemblyStep):
    failures = session.query(Failure).filter_by(assembly_step = step, failure_type = FailureType.not_moving_oc, is_verified=True).all()
    if len(failures) != 1: raise Exception("DataStruture is corrupt! There should be only 1 instance of failure for a given AssemblyStep with FailureType overcurrent.")
    return failures[0]



@catch_exceptions
def sorted_failures_by_incidents(session:Session, step:AssemblyStep):
    failures_without_oc: List[Failure] = session.query(Failure).\
        filter(
            Failure.failure_type != FailureType.overcurrent,
            Failure.failure_type != FailureType.not_moving_oc,
            Failure.assembly_step == step,
            Failure.is_verified == True,).all()
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
def get_improvements_for_failure(session:Session, step:AssemblyStep, fail:Failure) -> List[Improvement]:
    """Based on parameter fail, query not yet tried improvements for this current transmission.
    Set of not tried improvement is than sorted by global (over all transmissions) success rate (Based on ImprovementInstances).
    If success rate of 2 improvement equals, second sort-key is the total (global) number of ImprovementInstances of this improvement.  
    """
    
    def _sort_improvements_by_success_probability(improvements:Set[Improvement], session:Session):
        def _get_success_prop(element:Improvement, session:Session):
            ...
            num_total = session.query(ImprovementInstance).filter_by(improvement = element).count()
            if num_total == 0: return (0,0)
            num_success = session.query(ImprovementInstance).filter_by(improvement = element, successful = True).count()
            return (num_success/num_total, num_total)
        
        return sorted(improvements, key=lambda element: _get_success_prop(element, session), reverse=True)

    
    
    fail = session.query(Failure).get(fail.id)
    t = session.query(Transmission).order_by(Transmission.id.desc()).first()
    possible_improvements = set(fail.improvements)

    done_imp_instances:List[ImprovementInstance] = session.query(ImprovementInstance).filter_by(transmission = t, assembly_step = step).all()
    done_improvements = {instance.improvement for instance in done_imp_instances}

    improvements_not_tried_yet = possible_improvements - done_improvements
    sorted_items = _sort_improvements_by_success_probability(improvements_not_tried_yet, session)
    return sorted_items





@catch_exceptions
def delete_improvement_instance(session:Session, imp_instance: ImprovementInstance):
    # session = get_session()
    session.delete(imp_instance)
    session.commit()



@catch_exceptions
def setup_improvement_start(session:Session, t:Transmission, failure:Failure, improvement:Improvement, m:Measurement, assembly_step:AssemblyStep) -> Tuple[FailureInstance, ImprovementInstance]:
    """Setup all necessary objects for improvement!"""
    t = session.query(Transmission).get(t.id)
    failure = session.query(Failure).get(failure.id)
    m = session.query(Measurement).get(m.id)

    failure_instance = FailureInstance(failure = failure, measurement=m, assembly_step = assembly_step)
    t.failure_instances.append(failure_instance)
    improvement_instance = ImprovementInstance(improvement = improvement, failure_instance=failure_instance, assembly_step = assembly_step)
    t.improvement_instances.append(improvement_instance)
    session.commit()
    logger.warning("IS FAILURE_INSTANCE.MEASUREMENT == NULL???")
    logger.warning(failure_instance.measurement)
    return failure_instance, improvement_instance


@catch_exceptions
def cancel_improvement(session:Session, fail_instance: FailureInstance, imp_instance:ImprovementInstance):
    """If improvement gets canceld, remove failure instance and improvement instance created prior with setup_improvement_start()."""
    session.delete(fail_instance)
    session.delete(imp_instance)
    session.commit()


@catch_exceptions
def set_success_status(session:Session, imp_instance:ImprovementInstance, status:bool):
    imp_instance = session.query(ImprovementInstance).get(imp_instance.id)
    imp_instance.successful = status
    session.commit()
    session.flush()
    return imp_instance

@catch_exceptions
def update_improvement_measurement_relation(session:Session, m:Measurement, imp_instance:ImprovementInstance):
    imp_instance = session.query(ImprovementInstance).get(imp_instance.id)
    imp_instance.measurement = m
    session.commit()


@catch_exceptions
def refresh_improvement_instance(session:Session, id):
    ...
    return session.query(ImprovementInstance).get(id)
