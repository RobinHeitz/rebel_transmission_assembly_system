# %%
from sqlalchemy.orm.session import Session
import sqlalchemy as db

from data_management.model import Failure, FailureType, Transmission, TransmissionConfiguration, AssemblyStep
from data_management.model import Measurement, Assembly, AssemblyStep, DataPoint
from data_management.model import Failure, FailureInstance, Improvement, ImprovementInstance

import random

engine, connection, metadata, session = None, None, None, None

def add_to_session(session:Session, *args):
    for i in args:
        session.add(i)

def setup_session():
    global engine, connection, metadata, session

    engine = db.create_engine('sqlite:///rebel.sqlite')
    connection = engine.connect()
    metadata = db.MetaData()
    session = sessionmaker(bind = engine)()


# def test(session:Session, t:Transmission, assembly_step: AssemblyStep):
#     ...
#     ind_1 = Indicator(description = "Strom > Nennwert", assembly_step = assembly_step, indicator_type = IndicatorType.overcurrent)
#     ind_2 = Indicator(description = "Module Dead: Wicklungsfehler?", assembly_step = assembly_step, indicator_type = IndicatorType.not_measurable)
#     ind_3 = Indicator(description = "Encoderfehler", assembly_step = assembly_step, indicator_type = IndicatorType.not_measurable)
#     session.add(ind_1)
#     session.add(ind_2)
#     session.add(ind_3)

#     fail_1 = Failure(description = "Fehler-Kategorie 1", assembly_step = assembly_step)
#     session.add(fail_1)
#     fail_1.indicators.append(ind_1)
#     fail_1.indicators.append(ind_3)

#     fail_2 = Failure(description = "Fehler-Kategorie 2", assembly_step = assembly_step)
#     session.add(fail_2)
#     fail_2.indicators.append(ind_1)
#     fail_2.indicators.append(ind_2)
    
#     fail_3 = Failure(description = "Fehler-Kategorie 3", assembly_step = assembly_step)
#     session.add(fail_3)
#     fail_3.indicators.append(ind_3)
#     fail_3.indicators.append(ind_2)

#     imp_1 = Improvement(description="Improvement Methode 1", assembly_step = assembly_step)
#     session.add(imp_1)
#     imp_2 = Improvement(description="Improvement Methode 2", assembly_step = assembly_step)
#     session.add(imp_2)
#     imp_3 = Improvement(description="Improvement Methode 3", assembly_step = assembly_step)
#     session.add(imp_3)
#     imp_4 = Improvement(description="Improvement Methode 4", assembly_step = assembly_step)
#     session.add(imp_4)
#     imp_5 = Improvement(description="Improvement Methode 5", assembly_step = assembly_step)
#     session.add(imp_5)

#     fail_1.improvements.append(imp_1)
#     fail_1.improvements.append(imp_3)
    
#     fail_2.improvements.append(imp_2)
#     fail_2.improvements.append(imp_4)
    
#     fail_3.improvements.append(imp_4)
#     fail_3.improvements.append(imp_5)
#     fail_3.improvements.append(imp_1)

#     # Create Indicator-/ Failure-/ Improvement - Instances!

#     i_ind_1 = IndicatorInstance(indicator=ind_1, transmission = t)
#     i_ind_2 = IndicatorInstance(indicator=ind_3, transmission = t)
#     session.add(i_ind_1)
#     session.add(i_ind_2)
    
#     i_fail_1 = FailureInstance(failure=fail_1, transmission = t)
#     i_fail_2 = FailureInstance(failure=fail_2, transmission = t)
#     session.add(i_fail_1)
#     session.add(i_fail_2)
    
#     i_imp_1 = ImprovementInstance(improvement=imp_3, transmission=t, successful=True)
#     i_imp_2 = ImprovementInstance(improvement=imp_4, transmission=t, successful=False)
#     i_imp_3 = ImprovementInstance(improvement=imp_1, transmission=t, successful=False)

#     session.add(i_imp_1)
#     session.add(i_imp_2)
#     session.add(i_imp_3)



def create_assembly_step_1(session:Session, t:Transmission, assembly_step:AssemblyStep):
    f1 = Failure(description="Strom > Nennwert", assembly_step = assembly_step, failure_type = FailureType.overcurrent)
    f2 = Failure(description="Encoderfehler", assembly_step = assembly_step, failure_type = FailureType.overcurrent)
    f3 = Failure(description="Ruckeln beim Anfahren", assembly_step = assembly_step, failure_type = FailureType.overcurrent)
    f4 = Failure(description="OC beim Anfahren", assembly_step = assembly_step, failure_type = FailureType.overcurrent)
    f5 = Failure(description="Module Dead: Wicklungsfehler??", assembly_step = assembly_step, failure_type = FailureType.overcurrent)

    add_to_session(session, f1, f2, f3, f4, f5)

    imp_1 = Improvement(description = "Motor tauschen", assembly_step = assembly_step)
    imp_2 = Improvement(description = "Encoder tauschen", assembly_step = assembly_step)
    imp_3 = Improvement(description = "Kabel verbinden/ tauschen", assembly_step = assembly_step)
    imp_4 = Improvement(description = "Paramter auf Controller updaten", assembly_step = assembly_step)
    imp_5 = Improvement(description = "Encoder & Halter auf Welle pressen", assembly_step = assembly_step)
    imp_6 = Improvement(description = "Bremse tauschen", assembly_step = assembly_step)

    add_to_session(session, imp_1, imp_2, imp_3, imp_4, imp_5, imp_6)
    
    f1.improvements.append(imp_1)

    # f2.improvements.append(imp_2)
    # f2.improvements.append(imp_3)
    f2.improvements = [imp_2, imp_3]
    
    f3.improvements = [imp_4, imp_5]

    f4.improvements = [imp_4, imp_6]
    
    f5.improvements = [imp_1]
    # f3.improvements(imp_1)
    # f4.improvements(imp_1)
    # f5.improvements(imp_1)
    


    
    # ind_1 = Indicator(description = "Module Dead: Wicklungsfehler?", assembly_step = assembly_step, indicator_type = IndicatorType.not_measurable)
    # ind_2 = Indicator(description = "Strom > Nennwert", assembly_step = assembly_step, indicator_type = IndicatorType.overcurrent)
    # ind_3 = Indicator(description = "Encoderfehler", assembly_step = assembly_step, indicator_type = IndicatorType.not_measurable)
    # ind_4 = Indicator(description = "Ruckeln beim Anfahren", assembly_step = assembly_step, indicator_type = IndicatorType.not_measurable)
    # ind_5 = Indicator(description = "OC beim anfahren", assembly_step = assembly_step, indicator_type = IndicatorType.not_measurable)

    # add_to_session(session, ind_1, ind_2, ind_3, ind_4, ind_5)

    # fail_1 = Failure(description = "Wicklungsfehler Motorspule", assembly_step = assembly_step)
    # fail_2 = Failure(description = "Motor entspricht nicht der geforderten Qualität", assembly_step = assembly_step)
    # fail_3 = Failure(description = "Encoder defekt", assembly_step = assembly_step)
    # fail_4 = Failure(description = "Encoderkabel defekt", assembly_step = assembly_step)
    # fail_5 = Failure(description = "Encoderkabel nicht verbunden", assembly_step = assembly_step)
    # fail_6 = Failure(description = "Falsche Parameter/ FW", assembly_step = assembly_step)
    # fail_7 = Failure(description = "Abstand Encoder/ Magnetring (Rotor) falsch", assembly_step = assembly_step)
    # fail_8 = Failure(description = "Bremse löst nicht", assembly_step = assembly_step)
    
    # add_to_session(session, fail_1, fail_2, fail_3, fail_4, fail_5, fail_6, fail_7)

    # imp_1 = Improvement(description = "Motor tauschen", assembly_step = assembly_step)
    # imp_2 = Improvement(description = "Encoder tauschen", assembly_step = assembly_step)
    # imp_3 = Improvement(description = "Kabel verbinden/ tauschen", assembly_step = assembly_step)
    # imp_4 = Improvement(description = "Paramter auf Controller updaten", assembly_step = assembly_step)
    # imp_5 = Improvement(description = "Encoder & Halter auf Welle pressen", assembly_step = assembly_step)
    # imp_6 = Improvement(description = "Bremse tauschen", assembly_step = assembly_step)

    # add_to_session(session, imp_1, imp_2, imp_3, imp_4, imp_5, imp_6)

    # # Connect objects
    # fail_1.indicators.append(ind_1)
    # fail_1.improvements.append(imp_1)

    # fail_2.indicators.append(ind_2)
    # fail_2.improvements.append(imp_1)

    # fail_3.indicators.append(ind_3)
    # fail_3.improvements.append(imp_2)

    # fail_4.indicators.append(ind_3)
    # fail_4.improvements.append(imp_3)

    # fail_5.indicators.append(ind_3)
    # fail_5.improvements.append(imp_3)

    # fail_6.indicators.append(ind_4)
    # fail_6.improvements.append(imp_4)
    
    # fail_7.indicators.append(ind_4)
    # fail_7.improvements.append(imp_5)

    # fail_8.indicators.append(ind_5)
    # fail_8.improvements.append(imp_4)
    # fail_8.improvements.append(imp_6)

# def create_assembly_step_1_old(session:Session, t:Transmission, assembly_step:AssemblyStep):
#     ind_1 = Indicator(description = "Module Dead: Wicklungsfehler?", assembly_step = assembly_step, indicator_type = IndicatorType.not_measurable)
#     ind_2 = Indicator(description = "Strom > Nennwert", assembly_step = assembly_step, indicator_type = IndicatorType.overcurrent)
#     ind_3 = Indicator(description = "Encoderfehler", assembly_step = assembly_step, indicator_type = IndicatorType.not_measurable)
#     ind_4 = Indicator(description = "Ruckeln beim Anfahren", assembly_step = assembly_step, indicator_type = IndicatorType.not_measurable)
#     ind_5 = Indicator(description = "OC beim anfahren", assembly_step = assembly_step, indicator_type = IndicatorType.not_measurable)

#     add_to_session(session, ind_1, ind_2, ind_3, ind_4, ind_5)

#     fail_1 = Failure(description = "Wicklungsfehler Motorspule", assembly_step = assembly_step)
#     fail_2 = Failure(description = "Motor entspricht nicht der geforderten Qualität", assembly_step = assembly_step)
#     fail_3 = Failure(description = "Encoder defekt", assembly_step = assembly_step)
#     fail_4 = Failure(description = "Encoderkabel defekt", assembly_step = assembly_step)
#     fail_5 = Failure(description = "Encoderkabel nicht verbunden", assembly_step = assembly_step)
#     fail_6 = Failure(description = "Falsche Parameter/ FW", assembly_step = assembly_step)
#     fail_7 = Failure(description = "Abstand Encoder/ Magnetring (Rotor) falsch", assembly_step = assembly_step)
#     fail_8 = Failure(description = "Bremse löst nicht", assembly_step = assembly_step)
    
#     add_to_session(session, fail_1, fail_2, fail_3, fail_4, fail_5, fail_6, fail_7)

#     imp_1 = Improvement(description = "Motor tauschen", assembly_step = assembly_step)
#     imp_2 = Improvement(description = "Encoder tauschen", assembly_step = assembly_step)
#     imp_3 = Improvement(description = "Kabel verbinden/ tauschen", assembly_step = assembly_step)
#     imp_4 = Improvement(description = "Paramter auf Controller updaten", assembly_step = assembly_step)
#     imp_5 = Improvement(description = "Encoder & Halter auf Welle pressen", assembly_step = assembly_step)
#     imp_6 = Improvement(description = "Bremse tauschen", assembly_step = assembly_step)

#     add_to_session(session, imp_1, imp_2, imp_3, imp_4, imp_5, imp_6)

#     # Connect objects
#     fail_1.indicators.append(ind_1)
#     fail_1.improvements.append(imp_1)

#     fail_2.indicators.append(ind_2)
#     fail_2.improvements.append(imp_1)

#     fail_3.indicators.append(ind_3)
#     fail_3.improvements.append(imp_2)

#     fail_4.indicators.append(ind_3)
#     fail_4.improvements.append(imp_3)

#     fail_5.indicators.append(ind_3)
#     fail_5.improvements.append(imp_3)

#     fail_6.indicators.append(ind_4)
#     fail_6.improvements.append(imp_4)
    
#     fail_7.indicators.append(ind_4)
#     fail_7.improvements.append(imp_5)

#     fail_8.indicators.append(ind_5)
#     fail_8.improvements.append(imp_4)
#     fail_8.improvements.append(imp_6)





from sqlalchemy.orm import sessionmaker

if __name__ == "__main__":

    setup_session()


    model_classes = [Transmission, Assembly, Measurement, DataPoint, Failure, FailureInstance, Improvement, ImprovementInstance]

    objects_to_delete = [i for c in model_classes for i in session.query(c).all()]
    for i in objects_to_delete:
        session.delete(i)
    
    session.flush()

    # Transmission

    t = Transmission(transmission_configuration = TransmissionConfiguration.config_105_break_encoder)
    session.add(t)


    create_assembly_step_1(session, t, AssemblyStep.step_1_no_flexring)
    # test(session, t, AssemblyStep.step_1_no_flexring)
    session.commit()



