from sqlalchemy import Column, Integer, String, ForeignKey, Table, Enum, DateTime, Float, Boolean
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
    __tablename__ = "transmission"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    transmission_configuration = Column(Enum(TransmissionConfiguration))
    finished_date = Column(DateTime)
    
    assemblies = relationship("Assembly", backref=backref("transmission"))
    
    # indicator_instances = relationship("IndicatorInstance", backref=backref("transmission"))
    failure_instances = relationship("FailureInstance", backref=backref("transmission"))
    improvement_instances = relationship("ImprovementInstance", backref=backref("transmission"))
    

class Assembly(Base):
    __tablename__ = "assembly"
    created_at = Column(DateTime, default=datetime.now)
    id = Column(Integer, primary_key=True)

    assembly_step = Column(Enum(AssemblyStep))
    
    transmission_id = Column(Integer, ForeignKey("transmission.id"))
    measurements = relationship("Measurement", backref=backref("assembly"))

    def __repr__(self) -> str:
        return f"Assembly: {self.assembly_step}"


class Measurement(Base):
    __tablename__ = "measurement"

    # ToDO: Add meta data about measure: Duration, Which speed, was measurement ok?
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now)

    max_current = Column(Float)
    min_current = Column(Float)
    mean_current = Column(Float)

    assembly_id = Column(Integer, ForeignKey("assembly.id"))
    datapoints = relationship("DataPoint", backref=backref("measurement"))

    def __repr__(self):
        return f"Measurement-Instance: mean current = {self.mean_current} | # DataPoints: {len(self.datapoints)} "



class DataPoint(Base):
    __tablename__ = "datapoint"
    id = Column(Integer, primary_key = True)
    created_at = Column(DateTime, default=datetime.now)
    
    current = Column(Float)
    timestamp = Column(Float)

    measurement_id = Column(Integer, ForeignKey("measurement.id"))


# class IndicatorType(enum.Enum):
#     overcurrent = 1
#     calibration_both_tracks_values =  2

#     not_measurable = 10

class FailureType(enum.Enum):
    overcurrent = 1
    calibration_both_tracks_values =  2

    not_measurable = 10


# IndicatorFailureTable = Table(
#     'IndicatorFailureTable',
#     Base.metadata,
#     Column('id', Integer, primary_key=True),
#     Column('indicatorID', Integer, ForeignKey('indicator.id')),
#     Column('failureID', Integer, ForeignKey('failure.id')),
# )


FailureImprovementTable = Table(
    'FailureImprovementTable',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('failureID', Integer, ForeignKey('failure.id')),
    Column('improvementID', Integer, ForeignKey('improvement.id')),
)


# class Indicator(Base):
#     __tablename__ = 'indicator'
#     id = Column(Integer, primary_key=True)
#     created_at = Column(DateTime, default=datetime.now)
#     description = Column(String)
#     assembly_step = Column(Enum(AssemblyStep))

#     indicator_type = Column(Enum(IndicatorType), default = IndicatorType.not_measurable)
#     indicator_instances = relationship("IndicatorInstance", backref=backref("indicator"))
    
#     failures = relationship('Failure', secondary=IndicatorFailureTable, back_populates="indicators")

#     def __repr__(self):
#         return f"Indicator-instance: {self.description}"


# class IndicatorInstance(Base):
#     __tablename__ = "indicatorinstance"
#     id = Column(Integer, primary_key = True)
#     indicator_id = Column(Integer, ForeignKey("indicator.id"))
#     transmission_id = Column(Integer, ForeignKey("transmission.id"))



class Failure(Base):
    __tablename__ = 'failure'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now)
    description = Column(String)
    assembly_step = Column(Enum(AssemblyStep))

    failure_type = Column(Enum(FailureType), default=FailureType.not_measurable)    
    failure_instances = relationship("FailureInstance", backref=backref("failure"))
    
    # indicators = relationship('Indicator', secondary=IndicatorFailureTable, back_populates="failures")
    improvements = relationship('Improvement', secondary=FailureImprovementTable, back_populates="failures")

    def __repr__(self):
        return f"Failure-instance: {self.description}"
    def __str__(self):
        return self.description


class FailureInstance(Base):
    __tablename__ = "failureinstance"
    id = Column(Integer, primary_key = True)
    failure_id = Column(Integer, ForeignKey("failure.id"))
    transmission_id = Column(Integer, ForeignKey("transmission.id"))


class Improvement(Base):
    __tablename__ = "improvement"
    id = Column(Integer, primary_key = True)
    created_at = Column(DateTime, default=datetime.now)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    assembly_step = Column(Enum(AssemblyStep))
    
    improvement_instances = relationship("ImprovementInstance", backref=backref("improvement"))
    failures = relationship('Failure', secondary=FailureImprovementTable, back_populates="improvements")

    def __repr__(self):
        return f"Improvement-instance: {self.title}"

    def __str__(self):
        return self.title


class ImprovementInstance(Base):
    __tablename__ = "improvementinstance"
    id = Column(Integer, primary_key = True)
    improvement_id = Column(Integer, ForeignKey("improvement.id"))
    transmission_id = Column(Integer, ForeignKey("transmission.id"))
    successful = Column(Boolean)

    def __str__(self):
        return f"ImprovementInstance: Improvement-ID = {self.improvement_id} | Transmission-ID = {self.transmission_id}"

