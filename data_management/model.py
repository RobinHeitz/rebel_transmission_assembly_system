from sqlalchemy import Column, Integer, String, ForeignKey, Table, Enum, DateTime, Float
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import func 
import enum
from datetime import datetime
from sqlalchemy.orm import session 

Base = declarative_base()

####################
### ENUM CLASSES ###
####################

class TransmissionConfiguration(enum.Enum):
    config_80 = 1
    config_80_encoder = 2

    config_105 = 3
    config_105_break = 4
    config_105_encoder = 5
    config_105_break_encoder = 6

    @classmethod
    def get_all_configs(cls):
        return [cls.config_80, cls.config_80_encoder, cls.config_105, cls.config_105_break, cls.config_105_encoder, cls.config_105_break_encoder]


class AssemblyStep(enum.Enum):
    step_1_no_flexring = 1
    step_2_with_flexring = 2
    step_3_gearoutput_not_screwed = 3
    step_4_gearoutput_screwed = 4

    @classmethod
    def get_all_steps(cls):
        return [cls.step_1_no_flexring, cls.step_2_with_flexring, cls.step_3_gearoutput_not_screwed, cls.step_4_gearoutput_screwed]



#####################
### MODEL CLASSES ###
#####################

# TODOS:
# - ERROR/ FAILURE CLS
# - CORRECTIVE ACTION (Behebungsmaßnahme)



class Transmission(Base):
    """
    Transmission model cls (SQLAlchemy).
    Params:
    - transmission_id (auto generated): Integer
    - created_at (auto generated): DateTime
    - updated_at (auto generated): DateTime
    - transmission_configuration: TransmissionConfiguration
    - finished_date: DateTime
    - assemblies (auto generated): List of Assembly-Objects (backref relation)"""

    __tablename__ = "transmission"
    transmission_id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    transmission_configuration = Column(Enum(TransmissionConfiguration))
    finished_date = Column(DateTime)
    
    assemblies = relationship("Assembly", backref=backref("transmission"))
    failures = relationship("Failure", backref=backref("transmission"))
    



class Assembly(Base):
    """
    Assembly model cls (SQLAlchemy).
    Params:
    - assmebly_id (auto generated): Integer
    - created_at (auto generated): DateTime
    - assembly_step: AssemblyStep
    - transmission_id (auto generated): Integer(Transmission Object)
    - measurements: List of Measurement-Objects (backref relation)"""

    __tablename__ = "assembly"
    created_at = Column(DateTime, default=datetime.now)
    assembly_id = Column(Integer, primary_key=True)

    assembly_step = Column(Enum(AssemblyStep))
    
    transmission_id = Column(Integer, ForeignKey("transmission.transmission_id"))
    measurements = relationship("Measurement", backref=backref("assembly"))
    
    

    def __repr__(self) -> str:
        return f"Assembly: {self.assembly_step}"



class Measurement(Base):
    """
    Measurement model cls (SQLAlchemy).
    Params:
    - measurement_id (auto generated): Integer
    - title: String
    - assembly_id: Assembly Object (ForeignKey)
    - datapoints: List of DataPoint-Objects (backref relation)"""
    
    __tablename__ = "measurement"

    # ToDO: Add meta data about measure: Duration, Which speed, was measurement ok?
    measurement_id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now)

    max_current = Column(Float)
    min_current = Column(Float)

    

    assembly_id = Column(Integer, ForeignKey("assembly.assembly_id"))
    datapoints = relationship("DataPoint", backref=backref("measurement"))

    def update_calculated_values(session:session.Session):
        ...
        
        max_current_point = session.query(func.max("datapoint.current")).first()
        min_current_point = session.query(func.min("datapoint.current")).first()

        return max_current_point, min_current_point

    def __repr__(self):
        return f"Measurement-Instance."



class DataPoint(Base):
    """
    DataPoint model cls (SQLAlchemy).
    Params:
    - datapoint_id (auto generated): Integer
    - current: Integer
    - timestamp: Integer
    - measurement_id: Integer(Measurement Object)"""

    __tablename__ = "datapoint"
    datapoint_id = Column(Integer, primary_key = True)
    created_at = Column(DateTime, default=datetime.now)
    
    current = Column(Float)
    timestamp = Column(Float)

    measurement_id = Column(Integer, ForeignKey("measurement.measurement_id"))



class Failure(Base):
    """Failure model cls (SQLAlchemy). Every occuring error/ failure at each assembly step is represented by this instance. 
    
    """
    __tablename__ = "failure"
    failure_id = Column(Integer, primary_key = True)
    
    failure_type = Column(Integer, ForeignKey("failuretype.failuretype_id"))
    transmission_id = Column(Integer, ForeignKey("transmission.transmission_id"))
    

class FailureType(Base):
    """Failure type model cls (SQLAlchemy). Needed for dynamically add failure kinds/ types to the application. Every occuring failure is linked to a failure type, 
    thus its possible to query for all failures for a given failure type.

    Params:
    - failure_type_id (auto generated): Integer
    - description: String
    - assembly_step: 
    
    """

    __tablename__ = "failuretype"
    failuretype_id = Column(Integer, primary_key = True)
    description = Column(String)
    
    assembly_step = Column(Enum(AssemblyStep))

    failures = relationship("Failure", backref=backref("failuretype"))


class CorrectiveAction(Base):
    """CorrectiveAction model cls (SQLAlchemy).
    
    """
    __tablename__ = "correctiveaction"
    corrective_action_id = Column(Integer, primary_key = True)