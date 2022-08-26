# %%

import sqlalchemy as db

from data_management.model import Failure, IndicatorType, Transmission, TransmissionConfiguration, AssemblyStep
from data_management.model import Measurement, Assembly, AssemblyStep, DataPoint, Indicator, Failure, Improvement

import random

engine, connection, metadata, session = None, None, None, None


def setup_session():
    global engine, connection, metadata, session

    engine = db.create_engine('sqlite:///rebel.sqlite')
    connection = engine.connect()
    metadata = db.MetaData()
    session = sessionmaker(bind = engine)()
    


from sqlalchemy.orm import sessionmaker

if __name__ == "__main__":

    setup_session()


    model_classes = [Transmission, Assembly, Measurement, DataPoint, Indicator, Failure, Improvement]

    objects_to_delete = [i for c in model_classes for i in session.query(c).all()]
    for i in objects_to_delete:
        session.delete(i)
    
    session.flush()

    # Transmission

    indicator_descriptions = [
        "Schleifen/ zyklisches Klacken", 
        "Bewegung des Motors mit Steuerung nicht möglich", 
        "Encoder-Error in Anzeige", 
        "Ruckeln bei Bewegung des Motors", 
        "Stromverlauf schwankt zu stark", 
        "Abrieb (Magnetring)", 
        "Quietschen",
    ]

    indicators = []


    t = Transmission(transmission_configuration = TransmissionConfiguration.config_105_break_encoder)
    session.add(t)

    for step in AssemblyStep:

        a = Assembly(assembly_step = step, transmission = t)
        session.add(a)


        oc = Indicator(description = "Strom > Nennwert", assembly_step = step, indicator_type = IndicatorType.overcurrent)
        session.add(oc)
        indicators.append(oc)

        other_indicator_descriptions = random.sample(indicator_descriptions, 2)
        for i in other_indicator_descriptions:
            ind = Indicator(description = i, assembly_step = step, indicator_type = IndicatorType.not_measurable)
            session.add(ind)
            indicators.append(ind)



    ########################
    # create failure objects
    ########################

    failure_descriptions = [
        "Wicklungsfehler", 
        "Encoder Defekt", 
        "Encoderkabel defekt",
        "Abstand zwischen Encoder und Rotor zu groß",
        "Zylinderrollenlager (Kunststoff) defekt/ Klemmt",
        "Dicke des Flexrings zu hoch",
        "Zahnradeinleger nicht richtig montiert",
        "Fertigungsfehler Alugehäuse (Motorseitig)",
        "Fertigungsfehler Alugehäuse (Abtriebsseitig)",
        "Encoder schleift",
        "Flexring schleift",
    ]

    for ind in indicators:
        descriptions = random.sample(failure_descriptions, 2)
        for d in descriptions:

            f = Failure(transmission = t, description = random.choice(failure_descriptions))
            ind.failures.append(f)

            session.add(f)    
    
    
    session.commit()



