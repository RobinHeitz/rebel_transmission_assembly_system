from msilib.schema import Error
from data_management import data_controller
from data_management.model import AssemblyStep, Failure, FailureInstance, FailureType, Improvement, ImprovementInstance
from rich import print
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



def input_assembly_step() -> AssemblyStep:
    id = console.input("Which assembly step do you want to inspect? :smiley: Input id of desired step.\n")

    while True:
        try:
            step = AssemblyStep(int(id))
            break
        except Exception:
            id = console.input("[red]Wrong input![/red] You need to input the id of desired assembly step!\n")
    return step


def input_failure_detail_index(valid_indices: List[int]) -> Failure:
    id = console.input("Which failure do you want to change the verified status? Input id of failure.\n")
    while True:
        try:
            index_ = int(id)
            if index_ in valid_indices:
                return session.query(Failure).get(index_)
            else:
                raise Exception("Wront input!")

        except:
            id = console.input("[red]Wrong input![/red] You need to input the id of desired failure!\n")

def input_changed_verify_status() -> None:
    """User inputs new status for given failure."""
    id = console.input("To what verified status do you want to change the selected failure? Input 'True', 'False' or 'Cancel' to cancel the action.\n")
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
        exit()
    else:
        return answers[id]



@app.command()
def verify_failures():
    """Change is_verified - status of failures. If not verified (yet), failures are not displayed in the programm."""
    list_assembly_steps()
    step = input_assembly_step()
  
    session = data_controller.create_session()
    failures = session.query(Failure).filter_by(assembly_step = step, failure_type = FailureType.not_measurable).all()
    list_failures(failures)

    fail_indices = [f.id for f in failures]
    fail = input_failure_detail_index(fail_indices)
    new_verified = input_changed_verify_status()
    
    fail.is_verified = new_verified
    session.commit()
    print("[magenta]Changes are saved. Current database status:[/magenta]")
    list_failures(failures)

@app.command()
def verify_improvements():
    """Change is_verified - status of improvements. If not verified (yet), improvements are not displayed in the programm."""
    





    
    
    




if __name__ == "__main__":
    app()
