# %%

from data_management import data_controller

from data_management.model import Failure, FailureType, Improvement, AssemblyStep, ImprovementInstance, Transmission
from typing import Set, List
from sqlalchemy.orm.session import Session


def get_sorted_improvements_for_failure() -> List[Improvement]:
    """Filters for not done improvements. Returns then filtered, thus Improvement with highest success chances are at the top."""
    
    def _sort_improvements_by_success_probability(improvements:Set[Improvement], session:Session):
        def _get_success_prop(element:Improvement, session:Session):
            ...
            num_total = session.query(ImprovementInstance).filter_by(improvement = element).count()
            if num_total == 0: return 0
            num_success = session.query(ImprovementInstance).filter_by(improvement = element, successful = True).count()
            return num_success/num_total
        
        return sorted(improvements, key=lambda element: _get_success_prop(element, session), reverse=True)

    
    
    session = data_controller.create_session()
    step = AssemblyStep.step_1_no_flexring
    fail = session.query(Failure).filter_by(assembly_step = step, failure_type = FailureType.not_measurable).first()
    # fail = session.query(Failure).get(fail.id)
    t = session.query(Transmission).order_by(Transmission.id.desc()).first()
    print("Fails: ", fail, "t = ", t)

    
    
    possible_improvements = set(fail.improvements)
    print("possible imps: ", possible_improvements)

    done_imp_instances:List[ImprovementInstance] = session.query(ImprovementInstance).filter_by(transmission = t, assembly_step = step).all()
    print("imp_instances = ", done_imp_instances)

    done_improvements = {instance.improvement for instance in done_imp_instances}

    improvements_not_tried_yet = possible_improvements - done_improvements
    print("improvements not tried yet:")
    print(improvements_not_tried_yet)

    sorted_items = _sort_improvements_by_success_probability(improvements_not_tried_yet, session)

    print(sorted_items)
    return sorted_items





    # all_possible_improvements: Set[Improvement] = set(fail.improvements)
    # print("possible:", all_possible_improvements)

    
    # session.query(ImprovementInstance).filter_by(assembly_step = step, transmission = t).all()



sorted_ = get_sorted_improvements_for_failure()
print("*"*5)
print(sorted_)