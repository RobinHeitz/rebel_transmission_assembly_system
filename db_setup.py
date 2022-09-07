# %%
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
import sqlalchemy as db

from data_management.model import Failure, FailureType, Transmission, TransmissionConfiguration, AssemblyStep
from data_management.model import Measurement, Assembly, AssemblyStep, DataPoint
from data_management.model import Failure, FailureInstance, Improvement, ImprovementInstance

import random

from data_management import data_controller

engine, connection, metadata, session = None, None, None, None

def add_to_session(session:Session, *args):
    for i in args:
        session.add(i)

# def setup_session():
#     global engine, connection, metadata, session

#     engine = db.create_engine('sqlite:///rebel.sqlite')
#     connection = engine.connect()
#     metadata = db.MetaData()
#     session = sessionmaker(bind = engine)()


def create_assembly_step_1(session:Session, assembly_step:AssemblyStep):
    f1 = Failure(description="Strom > Nennwert", assembly_step = assembly_step, failure_type = FailureType.overcurrent)
    f2 = Failure(description="Encoderfehler", assembly_step = assembly_step, failure_type = FailureType.not_measurable)
    f3 = Failure(description="Ruckeln beim Anfahren", assembly_step = assembly_step, failure_type = FailureType.not_measurable)
    f4 = Failure(description="OC beim Anfahren", assembly_step = assembly_step, failure_type = FailureType.overcurrent_not_moving)
    f5 = Failure(description="Module Dead: Wicklungsfehler??", assembly_step = assembly_step, failure_type = FailureType.not_measurable)

    add_to_session(session, f1, f2, f3, f4, f5)

    imp_1 = Improvement(
        title = "Motor tauschen", 
        assembly_step = assembly_step, 
        description = "Zum Tauschend es Motors müssen die Schrauben auf der Unterseite gelöst werden. ACHTUNG: Der Bremskolben könnte dann herausfallen.")
    
    imp_2 = Improvement(
        title = "Encoder tauschen", 
        assembly_step = assembly_step,
        description = "Encoder mit Halter von Welle ziehen und neuen mit der Montagehülse auf die Welle pressen.")
    
    imp_3 = Improvement(
        title = "Kabel verbinden/ tauschen", 
        assembly_step = assembly_step,
        description = "Stecker am Encoder lösen, Kabel wechseln und einstecken. ACHTUNG: Auf Kabelführung achten, bei der das Kabel nicht gequetscht wird!")
    
    imp_4 = Improvement(
        title = "Paramter auf Controller updaten", 
        assembly_step = assembly_step,
        description = "Mithilfe von ModuleControl die Parameter updaten!")
    
    imp_5 = Improvement(
        title = "Encoder & Halter auf Welle pressen", 
        assembly_step = assembly_step,
        description = "Mit der Montagehülse Encoder tiefer pressen. Darauf achten, dass Encoder auf der Unterseite nicht über Magnetring schleift - Ansonsten sind unterlegscheiben erforderlich!")
    
    imp_6 = Improvement(
        title = "Bremse tauschen", 
        assembly_step = assembly_step,
        description = "Die Bremse durch drehen lösen und wechseln. ACHTUNG: Der Bremskolben samt Feder kann herausfallen!")

    imp_7 = Improvement(
        title = "Encoder verbinden", 
        assembly_step = assembly_step,
        description = "Der Encoder ist nicht mit dem Controller verbunden. Überprüfe, ob das 5-polige Kabel verbunden bzw. beschädigt ist.")
    
    add_to_session(session, imp_1, imp_2, imp_3, imp_4, imp_5, imp_6)
    
    f1.improvements = [imp_1,]

    f2.improvements = [imp_2, imp_3]
    
    f3.improvements = [imp_4, imp_5]

    f4.improvements = [imp_4, imp_6, imp_7]
    
    f5.improvements = [imp_1]
    

def create_instances(session:Session,t:Transmission):

    f = session.query(Failure).first()
    i = f.improvements[0]


    fail_instance = FailureInstance(transmission=t, failure=f)
    session.add(fail_instance)

    imp_instance = ImprovementInstance(transmission=t, failure_instance = fail_instance, improvement=i)
    session.add(imp_instance)


def test_sort_failures(session:Session):
    __dummy_failure_instances(session)
    __test_method(session)

def __dummy_failure_instances(session:Session):
    session = data_controller.get_session()

    failures = session.query(Failure).filter_by(assembly_step = AssemblyStep.step_1_no_flexring).all()

    for f in failures:
        for i in range(random.randint(5,50)):
            fi = FailureInstance(failure = f)
            session.add(fi)
    
    session.commit()
    



def __test_method(session):
    print("*"*10)
    print("Testing method!!!")

    failures = session.query(Failure).filter_by(assembly_step = AssemblyStep.step_1_no_flexring).all()
    for f in failures:
        q = session.query(FailureInstance).filter_by(failure=f)

        print("For Failure: ", f, " we have quantity: ", q.count())

    
    sorted_failures = data_controller.sorted_failures_by_incidents(AssemblyStep.step_1_no_flexring)


if __name__ == "__main__":

    # setup_session()

    # session = data_controller.create_session()

    with data_controller.session_context() as session:
        model_classes = [Transmission, Assembly, Measurement, DataPoint, Failure, FailureInstance, Improvement, ImprovementInstance]

        objects_to_delete = [i for c in model_classes for i in session.query(c).all()]
        for i in objects_to_delete:
            session.delete(i)
        
        session.flush()
        session.commit()

        create_assembly_step_1(session, AssemblyStep.step_1_no_flexring)


        # test_sort_failures(session)
        session.commit()



