# %%
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
import sqlalchemy as db

from data_management.model import Failure, FailureType, Transmission, TransmissionConfiguration, AssemblyStep
from data_management.model import Measurement, Assembly, AssemblyStep, DataPoint
from data_management.model import Failure, FailureInstance, Improvement, ImprovementInstance

import random

from data_management import data_controller

engine, connection, metadata, session = (None, )*4

def add_to_session(session:Session, *args):
    for i in args:
        session.add(i)


################################################
### Failures that occure in every assembly step:
################################################

_too_much_current = dict(description = "Strom > Nennwert", failure_type = FailureType.overcurrent, is_verified = True)
_not_moving_oc = dict(description = "Overcurrent (OC) beim Anfahren, Motor dreht sich nicht.", failure_type = FailureType.not_moving_oc, is_verified = True)



def create_assembly_step_1(session:Session):
    current_step = AssemblyStep.step_1_no_flexring
    
    failure_std_kwargs = dict(
        failure_type = FailureType.not_measurable,
        is_verified = True, 
        assembly_step = current_step,
    )

    improvement_std_kwargs = dict(
        is_verified = True, 
        assembly_step = current_step,
        
    )

    f_too_much_current = Failure(assembly_step = current_step, **_too_much_current)
    f_not_moving_oc = Failure(assembly_step = current_step, **_not_moving_oc)

    f_noise = Failure(description = "Beim Bewegen des Motors treten komische Geräusche wie knacken/ schleifen auf.", **failure_std_kwargs)

    add_to_session(session, f_too_much_current, f_not_moving_oc, f_noise)

    i_change_motor = Improvement(
        title="Motor tauschen", 
        description="Zum Tauschend es Motors müssen die Schrauben auf der Unterseite gelöst werden. ACHTUNG: Der Bremskolben könnte dann herausfallen.",
        cable_must_disconnected = True,
        **improvement_std_kwargs, 
    )

    i_change_encoder = Improvement(
        title="Encoder tauschen", 
        description="Den alten Encoder von Welle abziehen und mit neuem Encoder ersetzen. Anschließend müssen die Kabel verbunden werden.",
        cable_must_disconnected = True, 
        **improvement_std_kwargs, 
    )

    i_connect_encoder = Improvement(
        title="Encoder Verbindung überprüfen", 
        description="Überprüfe, ob der Encoder mit dem Controller verbunden ist. Eventuell ist das Kabel beschädigt, dann muss dieses ausgewechselt werden.",
        cable_must_disconnected = True, 
        image_filename = "gui/assembly_pictures/encoder_cable_connect.png",
        **improvement_std_kwargs, 
    )
    
    i_cable_encoder = Improvement(
        title="Encoder Kabel überprüfen", 
        description="Überprüfe, ob die Kabel des Encoders beschädigt sind, dann müssen dieses ausgewechselt werden.",
        cable_must_disconnected = True, 
        **improvement_std_kwargs, 
    )

    i_check_encoder_distance = Improvement(
        title="Abstand Encoder mit Polpaarring überprüfen", 
        description="Eventuell ist der Abstand von Encoder zum Polpaarring zu groß. Überprüfe, ob der Encoder bis zum Anschlag auf die Welle geschoben ist.",
        cable_must_disconnected = False, 
        **improvement_std_kwargs, 
    )
    
    i_tigthen_screw = Improvement(
        title="Prüfe Schraubverbindung des Motors", 
        description="Eventuell ist der Motor nicht fest angeschraubt oder sitzt schief, überprüfe die Einbaulage des Motors. ",
        cable_must_disconnected = False, 
        **improvement_std_kwargs, 
    )
    
    i_locking_ring = Improvement(
        title="Prüfe Sicherungsringe", 
        description="Eventuell sitzen die Sicherungsringe des Motors nicht richtig, überprüfe diese.",
        cable_must_disconnected = False, 
        **improvement_std_kwargs, 
    )

    add_to_session(session, i_change_motor,i_cable_encoder, i_change_encoder, i_connect_encoder, i_check_encoder_distance, i_locking_ring, i_tigthen_screw)

    f_too_much_current.improvements = [i_change_motor]
    f_not_moving_oc.improvements = [i_change_motor, i_change_encoder, i_connect_encoder, i_check_encoder_distance, i_cable_encoder]
    f_noise.improvements = [i_change_motor, i_tigthen_screw, i_locking_ring]

   
def create_assembly_step_2(session:Session):
    current_step = AssemblyStep.step_2_with_flexring
    
    failure_std_kwargs = dict(
        failure_type = FailureType.not_measurable,
        is_verified = True, 
        assembly_step = current_step,
    )

    improvement_std_kwargs = dict(
        is_verified = True, 
        assembly_step = current_step,
        
    )

    f_too_much_current = Failure(assembly_step = current_step, **_too_much_current)
    f_not_moving_oc = Failure(assembly_step = current_step, **_not_moving_oc)

    f_noise = Failure(description = "Beim Bewegen des Motors treten komische Geräusche wie knacken/ schleifen auf.", **failure_std_kwargs)

    add_to_session(session, f_too_much_current, f_not_moving_oc, f_noise)

    i_change_flexring = Improvement(
        title="Flexring tauschen", 
        description="Flexring per Hand oder mit einer Zange vorsichtig herausziehen.",
        cable_must_disconnected = False,
        **improvement_std_kwargs, 
    )
    
    i_change_nadelrollenlager = Improvement(
        title="Nadelrollenlager tauschen", 
        description="Nadelrollenlager prüfen und austauschen, wenn Nadelrollen klemmen. Zum herausnehmen am besten bei der Trennung anfangen.",
        cable_must_disconnected = False,
        **improvement_std_kwargs, 
    )
   
    i_change_zahnringeinleger = Improvement(
        title="Zahnringeinleger (Motorseite) tauschen", 
        description="Zahnringeinleger (Motorseite) überprüfen: Der Zahnring muss bündig eingepresst sein. Zum Auswechseln am besten von der Gegenseite herausdrücken.",
        cable_must_disconnected = True,
        **improvement_std_kwargs, 
    )
    
    # i_change_gehaeuse = Improvement(
    #     title="Gehäuseunterteil tauschen", 
    #     description="Gehäuseunterteil entspricht eventuell nicht den Toleranzen und verformt damit den Zahnradeinleger. Zum Tauschen muss unter anderem der Motor und die Bremse (ACHTUNG: Bremskolben + Feder lose) demontiert werden.",
    #     cable_must_disconnected = True,
    #     **improvement_std_kwargs, 
    # )

    i_change_encoder = Improvement(
        title="Encoder tauschen", 
        description="Den alten Encoder von Welle abziehen und mit neuem Encoder ersetzen. Anschließend müssen die Kabel verbunden werden.",
        cable_must_disconnected = True, 
        **improvement_std_kwargs, 
    )

    i_connect_encoder = Improvement(
        title="Encoder Verbindung überprüfen", 
        description="Überprüfe, ob der Encoder mit dem Controller verbunden ist. Eventuell ist das Kabel beschädigt, dann muss dieses ausgewechselt werden.",
        cable_must_disconnected = True, 
        image_filename = "gui/assembly_pictures/encoder_cable_connect.png",
        **improvement_std_kwargs, 
    )

    i_check_encoder_distance = Improvement(
        title="Abstand Encoder mit Polpaarring überprüfen", 
        description="Eventuell ist der Abstand von Encoder zum Polpaarring zu groß. Überprüfe, ob der Encoder bis zum Anschlag auf die Welle geschoben ist.",
        cable_must_disconnected = False, 
        **improvement_std_kwargs, 
    )
    
    i_tigthen_screw = Improvement(
        title="Prüfe Schraubverbindung des Motors", 
        description="Eventuell ist der Motor nicht fest angeschraubt oder sitzt schief, überprüfe die Einbaulage des Motors. ",
        cable_must_disconnected = False, 
        **improvement_std_kwargs, 
    )
    
    i_locking_ring = Improvement(
        title="Prüfe Sicherungsringe", 
        description="Eventuell sitzen die Sicherungsringe des Motors nicht richtig, überprüfe diese.",
        cable_must_disconnected = False, 
        **improvement_std_kwargs, 
    )

    add_to_session(session, i_change_flexring, i_change_nadelrollenlager, i_change_zahnringeinleger,  
    i_check_encoder_distance, i_connect_encoder, i_change_encoder, i_tigthen_screw, i_locking_ring)

    f_too_much_current.improvements = [i_change_flexring, i_change_nadelrollenlager, i_change_zahnringeinleger]
    f_not_moving_oc.improvements = [i_check_encoder_distance, i_connect_encoder, i_change_encoder]

    f_noise.improvements = [i_tigthen_screw, i_locking_ring]






def create_assembly_step_3(session:Session):
    current_step = AssemblyStep.step_3_gearoutput_not_screwed
    
    failure_std_kwargs = dict(
        failure_type = FailureType.not_measurable,
        is_verified = True, 
        assembly_step = current_step,
    )

    improvement_std_kwargs = dict(
        is_verified = True, 
        assembly_step = current_step,
        
    )

    f_too_much_current = Failure(assembly_step = current_step, **_too_much_current)
    f_not_moving_oc = Failure(assembly_step = current_step, **_not_moving_oc)

    f_noise = Failure(description = "Beim Bewegen des Motors treten komische Geräusche wie knacken/ schleifen auf.", **failure_std_kwargs)

    add_to_session(session, f_too_much_current, f_not_moving_oc, f_noise)

    i_change_flexring = Improvement(
        title="Flexring tauschen", 
        description="Flexring per Hand oder mit einer Zange vorsichtig herausziehen.",
        cable_must_disconnected = False,
        **improvement_std_kwargs, 
    )
    
    i_change_zahnringeinleger = Improvement(
        title="Zahnringeinleger (Motorseite) tauschen", 
        description="Zahnringeinleger (Motorseite) überprüfen: Der Zahnring muss bündig eingepresst sein. Zum Auswechseln am besten von der Gegenseite herausdrücken.",
        cable_must_disconnected = True,
        **improvement_std_kwargs, 
    )
    
    i_abtrieb = Improvement(
        title="Baugruppe 'Abtrieb' wechseln", 
        description="Probiere einen anderen Abtrieb aus.", 
        cable_must_disconnected = False,
        **improvement_std_kwargs, 
    )
    
    i_change_gehaeuse = Improvement(
        title="Gehäuseunterteil tauschen", 
        description="Gehäuseunterteil entspricht eventuell nicht den Toleranzen und verformt damit den Zahnradeinleger. Zum Tauschen muss unter anderem der Motor und die Bremse (ACHTUNG: Bremskolben + Feder lose) demontiert werden.",
        cable_must_disconnected = True,
        **improvement_std_kwargs, 
    )

    i_change_encoder = Improvement(
        title="Encoder tauschen", 
        description="Den alten Encoder von Welle abziehen und mit neuem Encoder ersetzen. Anschließend müssen die Kabel verbunden werden.",
        cable_must_disconnected = True, 
        **improvement_std_kwargs, 
    )

    i_connect_encoder = Improvement(
        title="Encoder Verbindung überprüfen", 
        description="Überprüfe, ob der Encoder mit dem Controller verbunden ist. Eventuell ist das Kabel beschädigt, dann muss dieses ausgewechselt werden.",
        cable_must_disconnected = True, 
        image_filename = "gui/assembly_pictures/encoder_cable_connect.png",
        **improvement_std_kwargs, 
    )

    i_check_encoder_distance = Improvement(
        title="Abstand Encoder mit Polpaarring überprüfen", 
        description="Eventuell ist der Abstand von Encoder zum Polpaarring zu groß. Überprüfe, ob der Encoder bis zum Anschlag auf die Welle geschoben ist.",
        cable_must_disconnected = False, 
        **improvement_std_kwargs, 
    )
    
    i_tigthen_screw = Improvement(
        title="Prüfe Schraubverbindung des Motors", 
        description="Eventuell ist der Motor nicht fest angeschraubt oder sitzt schief, überprüfe die Einbaulage des Motors. ",
        cable_must_disconnected = False, 
        **improvement_std_kwargs, 
    )
    
    i_locking_ring = Improvement(
        title="Prüfe Sicherungsringe", 
        description="Eventuell sitzen die Sicherungsringe des Motors nicht richtig, überprüfe diese.",
        cable_must_disconnected = False, 
        **improvement_std_kwargs, 
    )
   
    i_encoder_halter_falsch_verklebt = Improvement(
        title="Prüfe Verklebung Encoder und Halter", 
        description="Eventuell ist der Encoder nicht bündig mit dem Halter verklebt. Wenn es einen Spalt gibt (bereits 1 mm reicht), muss die Verklebung erneuert werden.",
        cable_must_disconnected = True, 
        **improvement_std_kwargs, 
    )
  
    i_encoder_pins_loetung = Improvement(
        title="Lötpins des Encoders schleifen auf Polpaarring", 
        description="Falls die Lötpins an der Encoderunterseite nicht entfernt wurden, schleifen sie auf dem Polpaarring. Mit einer Kneifzange können die Pins entfernt werden.",
        cable_must_disconnected = True, 
        **improvement_std_kwargs, 
    )
    
    i_encoder_unterlegscheibe = Improvement(
        title="Unterlegscheibe zwischen Encoder und Rotor", 
        description="Wenn die Chips des Encoders auf dem Rotor bzw. Polpaarring schleifen, kann eine entsprechende Unterlegscheibe verwendet werden.",
        cable_must_disconnected = True, 
        **improvement_std_kwargs, 
    )



    add_to_session(session, i_change_flexring, i_change_zahnringeinleger, i_abtrieb, i_change_gehaeuse, i_change_encoder, i_connect_encoder,
    i_check_encoder_distance, i_tigthen_screw, i_locking_ring, i_encoder_halter_falsch_verklebt, i_encoder_pins_loetung, i_encoder_unterlegscheibe)

    
    f_too_much_current.improvements = [i_change_flexring, i_change_zahnringeinleger, i_abtrieb, i_change_gehaeuse, 
        i_encoder_halter_falsch_verklebt, i_encoder_pins_loetung, i_encoder_unterlegscheibe]
    
    f_not_moving_oc.improvements = [i_change_encoder, i_connect_encoder, i_check_encoder_distance]

    f_noise.improvements = [i_abtrieb, i_tigthen_screw, i_locking_ring, ]





if __name__ == "__main__":

    with data_controller.session_context() as session:
        model_classes = [Transmission, Assembly, Measurement, DataPoint, Failure, FailureInstance, Improvement, ImprovementInstance]

        objects_to_delete = [i for c in model_classes for i in session.query(c).all()]
        for i in objects_to_delete:
            session.delete(i)
        
        session.flush()
        session.commit()

        create_assembly_step_1(session)
        create_assembly_step_2(session)
        create_assembly_step_3(session)


        session.commit()



