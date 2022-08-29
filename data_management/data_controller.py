from sqlalchemy.orm.session import Session
from sqlalchemy.orm import sessionmaker, scoped_session
import sqlalchemy as db

from data_management.model import Transmission, TransmissionConfiguration
from data_management.model import Measurement, Assembly, AssemblyStep, DataPoint
from data_management.model import Failure, FailureInstance, Improvement, ImprovementInstance

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



#####################
###  Transmission ###
#####################

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
    return session.query(Transmission).order_by(Transmission.id.desc()).first()


################
### Assembly ###
################


@create_session
def get_assembly_from_current_transmission(session:Session, step:AssemblyStep) -> Assembly:
    """Returns assembly (filtered by param: Step) from current transmission."""
    t = session.query(Transmission).order_by(Transmission.id.desc()).first()
    return session.query(Assembly).filter_by(transmission=t, assembly_step=step).first()


###################
### Measurement ###
###################

@create_session
def get_current_measurement_instance(session:Session) -> Measurement:
    return session.query(Measurement).order_by(Measurement.id.desc()).first()


@create_session
def create_measurement(session:Session, assembly:Assembly) -> Measurement:
    new_measure = Measurement(assembly = assembly)
    
    session.add(new_measure)
    session.commit()

    return new_measure


@create_session
def update_current_measurement_fields(session:Session):
    m = session.query(Measurement).order_by(Measurement.id.desc()).first()
    datapoints_ = session.query(DataPoint).filter_by(measurement=m)
    
    current_values = [dp.current for dp in datapoints_]
    m.max_current = round(max(current_values),2)
    m.min_current = round(min(current_values),2)
    m.mean_current = round(sum(current_values) / len(current_values) ,2)
    session.commit()


@create_session
def get_plot_data_for_current_measurement(session:Session)-> List[Tuple]:
    """Returns list of (timestamp, current) of current measurement for plotting."""
    m = get_current_measurement_instance()

    datapoints = session.query(DataPoint).filter_by(measurement=m)
    return [(d.timestamp, d.current) for d in datapoints]


##################
### DataPoints ###
##################


@create_session
def create_data_point(session:Session, current, timestamp, measurement:Measurement):
   
    dp = DataPoint(current = current, timestamp = timestamp, measurement = measurement)
    session.add(dp)
    session.commit()

    return dp


def create_data_point_to_current_measurement(current, timestamp):
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

@create_session
def get_failures_list_for_assembly_step(session:Session, step:AssemblyStep):
    failures = session.query(Failure).filter_by(assembly_step = step).all()
    if failures == None:
        return []
    return failures

@create_session
def create_failure_instance(session:Session, failure:Failure):
    f = FailureInstance(failure_id=failure.id, transmission = get_current_transmission(session))
    session.add(f)
    session.commit()
    return f


####################
### IMPROVEMENTS ###
####################

@create_session
def create_improvement_instance(session:Session, imp:Improvement):
    i = ImprovementInstance(improvement_id=imp.id, transmission=get_current_transmission(session))
    session.add(i)
    session.commit()
    return i, i.id

@create_session
def get_improvement_instance(session:Session, imp_id):
    return session.query(ImprovementInstance).get(imp_id)


@create_session
def get_improvements_for_failure(session:Session, fail:Failure):
    failure = session.query(Failure).get(fail.id)

    if failure == None:
        return []
    
    improvements = failure.improvements
    return improvements

@create_session
def delete_improvement_instance(session:Session, imp_id):
    imp = session.query(ImprovementInstance).get(imp_id)
    session.delete(imp)
    session.commit()