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
    failures = relationship("Failure", backref=backref("transmission"))
    

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
        return f"Measurement-Instance."



class DataPoint(Base):
    __tablename__ = "datapoint"
    id = Column(Integer, primary_key = True)
    created_at = Column(DateTime, default=datetime.now)
    
    current = Column(Float)
    timestamp = Column(Float)

    measurement_id = Column(Integer, ForeignKey("measurement.id"))


class IndicatorType(enum.Enum):
    overcurrent = 1
    calibration_both_tracks_values =  2

    not_measurable = 10


IndicatorFailureTable = Table(
    'IndicatorFailureTable',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('indicatorID', Integer, ForeignKey('indicator.id')),
    Column('failureID', Integer, ForeignKey('failure.id')),
)


FailureImprovementTable = Table(
    'FailureImprovementTable',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('failureID', Integer, ForeignKey('failure.id')),
    Column('improvementID', Integer, ForeignKey('improvement.id')),
)


class Indicator(Base):
    __tablename__ = 'indicator'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now)
    description = Column(String)

    assembly_step = Column(Enum(AssemblyStep))
    indicator_type = Column(Enum(IndicatorType), default = IndicatorType.not_measurable)
    
    failures = relationship('Failure', secondary=IndicatorFailureTable, back_populates="indicators")




class Failure(Base):
    __tablename__ = 'failure'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now)
    description = Column(String)
    
    indicators = relationship('Indicator', secondary=IndicatorFailureTable, back_populates="failures")
    improvements = relationship('Improvement', secondary=FailureImprovementTable, back_populates="failures")
    transmission_id = Column(Integer, ForeignKey('transmission.id'))





class Improvement(Base):
    __tablename__ = "improvement"
    id = Column(Integer, primary_key = True)
    created_at = Column(DateTime, default=datetime.now)
    description = Column(String)
    
    improvement_successfull = Column(Boolean)
    failures = relationship('Failure', secondary=FailureImprovementTable, back_populates="improvements")





# IndicatorFailure = Table(
#     "IndicatorFailure",
#     Base.metadata, 
#     Column("id", Integer, primary_key = True),
#     Column("indicator_id", Integer, ForeignKey("indicator.id")),
#     Column("failure_id", Integer, ForeignKey("failure.id")),
# )


# class Indicator(Base):
#     #Beispiel: Overcurrent in Montageschritt n
#     __tablename__ = "indicator"
#     id = Column(Integer, primary_key = True)
#     created_at = Column(DateTime, default=datetime.now)

#     description = Column(String)
#     assembly_step = Column(Enum(AssemblyStep))
#     indicator_type = Column(Enum(IndicatorType), default = IndicatorType.not_measurable)
#     failures = relationship("Failure", secondary=IndicatorFailure, backref="Indicator")




# class Failure(Base):
#     #Beispiel zu OC in Schritt n: Flexring falsch, Alufrästeil falsch etc.
#     __tablename__ = "failure"
#     id = Column(Integer, primary_key = True)

#     description = Column(String)
#     indicator = Column(Integer, ForeignKey("indicator.id"))
#     transmission = Column(Integer, ForeignKey("transmission.id"))
#     indicators = relationship("Indicator", secondary=IndicatorFailure, backref="Failure")



# FailureImprovement = Table("FailureImprovement", 
#     Column("id", Integer, primary_key = True),
#         Column("failure_id", Integer, ForeignKey("failure.id")),
#         Column("improvement_id", Integer, ForeignKey("improvement.id")),
# )


























# class FailureClassification(enum.Enum):
#     """Is the failure_type overcurrent or another failure? This classification makes sure, failures that can be measured (by data points) are mapped to the correct failure type."""
#     overcurrent = 1
#     calibration_both_tracks_have_values = 2

#     not_measurable = 10




# class Failure(Base):
#     """Failure model cls (SQLAlchemy). Every occuring error/ failure at each assembly step is represented by this instance. 
    
#     """
#     __tablename__ = "failure"
#     id = Column(Integer, primary_key = True)
    
#     failure_type_id = Column(Integer, ForeignKey("failure_type.id"))
#     transmission_id = Column(Integer, ForeignKey("transmission.id"))
    
# class FailureType(Base):
#     """Failure type model cls (SQLAlchemy). Needed for dynamically add failure kinds/ types to the application. Every occuring failure is linked to a failure type, 
#     thus its possible to query for all failures for a given failure type.

#     Params:
#     - id (auto generated): Integer
#     - failure_classification: Enum(FailureClassification) | Detects whether this failure can be auto-detected by comparing measurement-values.
#     - description: String
#     - assembly_step: 
    
#     """

#     __tablename__ = "failure_type"
#     id = Column(Integer, primary_key = True)
#     description = Column(String)

#     failure_classification = Column(Enum(FailureClassification), default = FailureClassification.not_measurable)

#     assembly_step = Column(Enum(AssemblyStep))

#     failures = relationship("Failure", backref=backref("failure_type"))


# class CorrectiveAction(Base):
#     """CorrectiveAction model cls (SQLAlchemy).
    
#     """
#     __tablename__ = "correctiveaction"
#     id = Column(Integer, primary_key = True)