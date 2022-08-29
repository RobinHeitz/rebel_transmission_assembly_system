# %%
from sqlalchemy.orm.session import Session
import sqlalchemy as db

from data_management.model import Failure, IndicatorType, Transmission, TransmissionConfiguration, AssemblyStep
from data_management.model import Measurement, Assembly, AssemblyStep, DataPoint
from data_management.model import Indicator, IndicatorInstance, Failure, FailureInstance, Improvement, ImprovementInstance

import random

engine, connection, metadata, session = None, None, None, None


def setup_session():
    global engine, connection, metadata, session

    engine = db.create_engine('sqlite:///rebel.sqlite')
    connection = engine.connect()
    metadata = db.MetaData()
    session = sessionmaker(bind = engine)()


def test(session:Session, t:Transmission, assembly_step: AssemblyStep):
    ...
    ind_1 = Indicator(description = "Strom > Nennwert", assembly_step = assembly_step, indicator_type = IndicatorType.overcurrent)
    ind_2 = Indicator(description = "Module Dead: Wicklungsfehler?", assembly_step = assembly_step, indicator_type = IndicatorType.not_measurable)
    ind_3 = Indicator(description = "Encoderfehler", assembly_step = assembly_step, indicator_type = IndicatorType.not_measurable)
    session.add(ind_1)
    session.add(ind_2)
    session.add(ind_3)

    fail_1 = Failure(description = "Fehler-Kategorie 1", assembly_step = assembly_step)
    session.add(fail_1)
    fail_1.indicators.append(ind_1)
    fail_1.indicators.append(ind_3)

    fail_2 = Failure(description = "Fehler-Kategorie 2", assembly_step = assembly_step)
    session.add(fail_2)
    fail_2.indicators.append(ind_1)
    fail_2.indicators.append(ind_2)
    
    fail_3 = Failure(description = "Fehler-Kategorie 3", assembly_step = assembly_step)
    session.add(fail_3)
    fail_3.indicators.append(ind_3)
    fail_3.indicators.append(ind_2)

    imp_1 = Improvement(description="Improvement Methode 1", assembly_step = assembly_step)
    session.add(imp_1)
    imp_2 = Improvement(description="Improvement Methode 2", assembly_step = assembly_step)
    session.add(imp_2)
    imp_3 = Improvement(description="Improvement Methode 3", assembly_step = assembly_step)
    session.add(imp_3)
    imp_4 = Improvement(description="Improvement Methode 4", assembly_step = assembly_step)
    session.add(imp_4)
    imp_5 = Improvement(description="Improvement Methode 5", assembly_step = assembly_step)
    session.add(imp_5)

    fail_1.improvements.append(imp_1)
    fail_1.improvements.append(imp_3)
    
    fail_2.improvements.append(imp_2)
    fail_2.improvements.append(imp_4)
    
    fail_3.improvements.append(imp_4)
    fail_3.improvements.append(imp_5)
    fail_3.improvements.append(imp_1)

    # Create Indicator-/ Failure-/ Improvement - Instances!

    i_ind_1 = IndicatorInstance(indicator=ind_1, transmission = t)
    i_ind_2 = IndicatorInstance(indicator=ind_3, transmission = t)
    session.add(i_ind_1)
    session.add(i_ind_2)
    
    i_fail_1 = FailureInstance(failure=fail_1, transmission = t)
    i_fail_2 = FailureInstance(failure=fail_2, transmission = t)
    session.add(i_fail_1)
    session.add(i_fail_2)
    
    i_imp_1 = ImprovementInstance(improvement=imp_3, transmission=t, successful=True)
    i_imp_2 = ImprovementInstance(improvement=imp_4, transmission=t, successful=False)
    i_imp_3 = ImprovementInstance(improvement=imp_1, transmission=t, successful=False)

    session.add(i_imp_1)
    session.add(i_imp_2)
    session.add(i_imp_3)



def create_assembly_step_1(session:Session, t:Transmission, assembly_step:AssemblyStep):
    ind_1 = Indicator(description = "Strom > Nennwert", assembly_step = assembly_step, indicator_type = IndicatorType.overcurrent)
    ind_2 = Indicator(description = "Module Dead: Wicklungsfehler?", assembly_step = assembly_step, indicator_type = IndicatorType.not_measurable)
    ind_3 = Indicator(description = "Encoderfehler", assembly_step = assembly_step, indicator_type = IndicatorType.not_measurable)
    ind_4 = Indicator(description = "Ruckeln beim Anfahren", assembly_step = assembly_step, indicator_type = IndicatorType.not_measurable)
    ind_5 = Indicator(description = "OC beim anfahren", assembly_step = assembly_step, indicator_type = IndicatorType.not_measurable)

    session.add(ind_1)
    session.add(ind_2)
    session.add(ind_3)
    session.add(ind_4)
    session.add(ind_5)

    fail_1 = Failure(description = "Wicklungsfehler Motorspule", transmission = t, assembly_step = assembly_step)
    fail_1 = Failure(description = "Wicklungsfehler Motorspule", transmission = t)
    
    session.add(fail_1)

    print("Fail.ind", fail_1.indicators)
    





from sqlalchemy.orm import sessionmaker

if __name__ == "__main__":

    setup_session()


    model_classes = [Transmission, Assembly, Measurement, DataPoint, Indicator, IndicatorInstance, Failure, FailureInstance, Improvement, ImprovementInstance]

    objects_to_delete = [i for c in model_classes for i in session.query(c).all()]
    for i in objects_to_delete:
        session.delete(i)
    
    session.flush()

    # Transmission

    t = Transmission(transmission_configuration = TransmissionConfiguration.config_105_break_encoder)
    session.add(t)


    # create_assembly_step_1(session, t, AssemblyStep.step_1_no_flexring)
    test(session, t, AssemblyStep.step_1_no_flexring)


    # indicator_descriptions = [
    #     "Schleifen/ zyklisches Klacken", 
    #     "Bewegung des Motors mit Steuerung nicht möglich", 
    #     "Encoder-Error in Anzeige", 
    #     "Ruckeln bei Bewegung des Motors", 
    #     "Stromverlauf schwankt zu stark", 
    #     "Abrieb (Magnetring)", 
    #     "Quietschen",
    # ]

    # indicators = []


    # for step in AssemblyStep:

    #     a = Assembly(assembly_step = step, transmission = t)
    #     session.add(a)


    #     oc = Indicator(description = "Strom > Nennwert", assembly_step = step, indicator_type = IndicatorType.overcurrent)
    #     session.add(oc)
    #     indicators.append(oc)

    #     other_indicator_descriptions = random.sample(indicator_descriptions, 2)
    #     for i in other_indicator_descriptions:
    #         ind = Indicator(description = i, assembly_step = step, indicator_type = IndicatorType.not_measurable)
    #         session.add(ind)
    #         indicators.append(ind)



    # ########################
    # # create failure objects
    # ########################

    # failure_descriptions = [
    #     "Wicklungsfehler", 
    #     "Encoder Defekt", 
    #     "Encoderkabel defekt",
    #     "Abstand zwischen Encoder und Rotor zu groß",
    #     "Zylinderrollenlager (Kunststoff) defekt/ Klemmt",
    #     "Dicke des Flexrings zu hoch",
    #     "Zahnradeinleger nicht richtig montiert",
    #     "Fertigungsfehler Alugehäuse (Motorseitig)",
    #     "Fertigungsfehler Alugehäuse (Abtriebsseitig)",
    #     "Encoder schleift",
    #     "Flexring schleift",
    # ]

    # for ind in indicators:
    #     descriptions = random.sample(failure_descriptions, 2)
    #     for d in descriptions:

    #         f = Failure(transmission = t, description = random.choice(failure_descriptions))
    #         ind.failures.append(f)

    #         session.add(f)    
    
    
    session.commit()



