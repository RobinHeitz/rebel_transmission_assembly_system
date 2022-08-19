from sqlalchemy import Column, Integer, String, ForeignKey, Table, Enum, DateTime
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
import enum
from datetime import datetime

Base = declarative_base()


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
        return [cls.step_1_no_flexring, cls.step_2_with_flexring]




class Transmission(Base):
    """
    Transmission model cls (SQLAlchemy).
    Params:
    - transmission_id (read-only): Integer
    - created_at (read-only): DateTime
    - updated_at (read-only): DateTime
    - transmission_configuration: TransmissionConfiguration
    - finished_date: DateTime
    - assemblies (read-only): List of Assembly-Objects (backref relation)"""

    __tablename__ = "transmission"
    transmission_id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    transmission_configuration = Column(Enum(TransmissionConfiguration))
    finished_date = Column(DateTime)
    
    assemblies = relationship("Assembly", backref=backref("transmission"))
    



class Assembly(Base):
    """
    Assembly model cls (SQLAlchemy).
    Params:
    - assmebly_id (read-only): Integer
    - created_at (read-only): DateTime
    - assembly_step: AssemblyStep
    - transmission_id (read-only): Integer(Transmission Object)
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
    - measurement_id (read-only): Integer
    - title: String
    - assembly_id: Assembly Object (ForeignKey)
    - datapoints: List of DataPoint-Objects (backref relation)"""
    
    __tablename__ = "measurement"
    measurement_id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now)
    
    title = Column(String)

    assembly_id = Column(Integer, ForeignKey("assembly.assembly_id"))
    datapoints = relationship("DataPoint", backref=backref("measurement"))

    def __repr__(self):
        return f"Measurement-Instance."



class DataPoint(Base):
    """
    DataPoint model cls (SQLAlchemy).
    Params:
    - datapoint_id (read-only): Integer
    - current: Integer
    - timestamp: Integer
    - measurement_id: Integer(Measurement Object)"""

    __tablename__ = "datapoint"
    datapoint_id = Column(Integer, primary_key = True)
    created_at = Column(DateTime, default=datetime.now)
    
    current = Column(Integer)
    timestamp = Column(Integer)

    measurement_id = Column(Integer, ForeignKey("measurement.measurement_id"))



