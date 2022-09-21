from msilib.schema import Class
from data_management import data_controller
from data_management.model import AssemblyStep, Failure, FailureInstance, FailureType, Improvement, ImprovementInstance
from rich import print
from rich.table import Row
from rich.table import Table
from rich.console import Console

from typing import List


import typer

app = typer.Typer()
console = Console()
session = data_controller.create_session()

def list_assembly_steps() -> Table:
    """Lists all assembly steps in a table and prints it to the console."""
    table = Table(title="Assembly Steps")
    table.add_column("id", justify="center", style="magenta")
    table.add_column("name", justify="left", style="cyan")

    for step in AssemblyStep:
        table.add_row(str(step.value), str(step))
    console.print(table)

def list_failures(failures:List[Failure]) -> None:
    """Lists failures in a table and prints it to the console."""
    
    table = Table(title=f"Failures")
    table.add_column("id", justify="left", style="cyan", no_wrap=True)
    table.add_column("verified", justify="center", style="red")
    table.add_column("created at", justify="left", style="green")
    table.add_column("description", justify="left", style="cyan")
    table.add_column("# Improvements", justify="center", style="magenta")

    for f in failures:
        table.add_row(
            str(f.id),
            str(f.is_verified), 
            f.created_at.strftime('%d. %b %y, %H:%M'),
            str(f.description), 
            str(len(f.improvements)), 
        )
    console.print(table)


def list_improvements(improvements:List[Improvement]) -> None:
    """Lists improvements in a table and prints it to the console."""
    
    table = Table(title=f"Improvements")
    table.add_column("id", justify="left", style="cyan", no_wrap=True)
    table.add_column("verified", justify="center", style="red", width=5)
    table.add_column("created at", justify="left", style="green", width=10)
    table.add_column("title", justify="left", style="cyan", width=20)
    table.add_column("description", justify="left", style="cyan")
    table.add_column("has img", justify="center", style="red")
    table.add_column("# Fails", justify="center", style="magenta", width=5)

    for i in improvements:
        table.add_row(
            str(i.id),
            str(i.is_verified), 
            i.created_at.strftime('%d. %b %y, %H:%M'),
            i.title, 
            i.description,
            str(i.image_filename != None),
            str(len(i.failures)),end_section=True,
        
        )
    console.print(table)



def input_assembly_step() -> AssemblyStep:
    id = console.input("Which assembly step do you want to inspect? :smiley: Input id of desired step.\n")

    while True:
        try:
            step = AssemblyStep(int(id))
            break
        except Exception:
            id = console.input("[red]Wrong input![/red] You need to input the id of desired assembly step!\n")
    return step


def input_detail_failure(valid_indices: List[int]) -> Failure:
    """Asks for id of a failure. If input is valid, returns Failure instance."""
    return __input_detail_index_of_type(Failure, valid_indices)

def input_detail_improvement(valid_indices: List[int]) -> Improvement:
    """Asks for id of a improvemnet. If input is valid, returns Improvement instance."""
    return __input_detail_index_of_type(Improvement, valid_indices)


def __input_detail_index_of_type(object_type, valid_indices: List[int]):
    type_name = str(object_type.__name__)
    
    id = console.input(f"Which {type_name} do you want to change the verified status? Input id of {type_name}.\n")
    while True:
        try:
            index_ = int(id)
            if index_ in valid_indices:
                return session.query(object_type).get(index_)
            else:
                raise Exception("Wront input!")

        except:
            id = console.input(f"[red]Wrong input![/red] You need to input the id of desired {type_name}!\n")

def input_changed_verify_status(model_object_type) -> None:
    """User inputs new status for given object type."""
    type_name = model_object_type.__name__
    id = console.input(f"To what verified status do you want to change the selected {type_name}? Input 'True', 'False' or 'Cancel' to cancel the action.\n")
    id = id.lower()

    while True:
        if id in ["true", "false", "cancel"]:
            ...
            break
        else:
            id = console.input("[red]Wrong input![/red] You need to input the the new value of <is verified>: 'True' or 'False'. Type 'Cancel' to abort!\n")

    answers = dict(
        true = True, 
        false = False,
    )
    if id == "cancel":
        __exit()
    else:
        return answers[id]


def __exit():
    session.close()
    exit()


@app.command()
def verify_failures():
    """Change is_verified - status of failures. If not verified (yet), failures are not displayed in the programm."""
    list_assembly_steps()
    step = input_assembly_step()
  
    failures = session.query(Failure).filter_by(assembly_step = step, failure_type = FailureType.not_measurable).all()
    list_failures(failures)

    fail_indices = [f.id for f in failures]
    fail = input_detail_failure(fail_indices)
    new_verified = input_changed_verify_status(Failure)
    fail.is_verified = new_verified
    
    session.commit()
    print("[magenta]Changes are saved. Current database status:[/magenta]")
    list_failures(failures)
    __exit()

@app.command()
def verify_improvements():
    """Change is_verified - status of improvements. If not verified (yet), improvements are not displayed in the programm."""
    list_assembly_steps()
    step = input_assembly_step()

    improvements = session.query(Improvement).filter_by(assembly_step = step).all()
    list_improvements(improvements)
    
    imp_indices = [i.id for i in improvements]
    improvement = input_detail_improvement(imp_indices)
    new_verified = input_changed_verify_status(Improvement)
    improvement.is_verified = new_verified

    session.commit()
    print("[magenta]Changes are saved. Current database status:[/magenta]")
    list_improvements(improvements)
    __exit()
    




    
    
    




if __name__ == "__main__":
    app()
