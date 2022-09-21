from msilib.schema import Error
from data_management import data_controller
from data_management.model import AssemblyStep, Failure, FailureInstance, Improvement, ImprovementInstance
from rich import print
from rich.table import Table
from rich.console import Console

from typing import List


import typer

app = typer.Typer()
console = Console()

def list_assembly_steps() -> Table:
    """Lists all assembly steps in a table and returns it then."""
    table = Table(title="Assembly Steps")
    table.add_column("id", justify="center", style="magenta")
    table.add_column("name", justify="left", style="cyan")

    for step in AssemblyStep:
        table.add_row(str(step.value), str(step))
    console.print(table)

def list_failures(failures:List[Failure]) -> None:
    """Lists failures in a table and returns it then."""
    
    table = Table(title=f"Failures")
    table.add_column("id", justify="left", style="cyan", no_wrap=True)
    table.add_column("verified", justify="center", style="red")
    table.add_column("created at", justify="left", style="green")
    table.add_column("description", justify="left", style="cyan")
    table.add_column("failure type", justify="left", style="green")
    table.add_column("# Improvements", justify="center", style="magenta")

    for f in failures:
        table.add_row(
            str(f.id),
            str(f.is_verified), 
            f.created_at.strftime('%d. %b %y, %H:%M'),
            str(f.description), 
            str(f.failure_type.name), 
            str(len(f.improvements)), 
        )
    console.print(table)


def input_assembly_step() -> AssemblyStep:
    table = list_assembly_steps()
    id = console.input("Which assembly step do you want to inspect? :smiley: Input id of desired step.")

    while True:
        try:
            step = AssemblyStep(int(id))
            break
        except Exception:
            id = console.input("[red]Wrong input![/red] You need to input the id of desired assembly step!")
    return step



@app.command()
def verify_failures():
    """Verifies created failures that are not yet accessable for others."""
    step = input_assembly_step()
    session = data_controller.create_session()
    failures = session.query(Failure).filter_by(assembly_step = step).all()
    list_failures(failures)



# @app.command()
# def list_fails(assembly_step: int):
#     session = data_controller.create_session()
    
#     try:
#         step = AssemblyStep(assembly_step)
#     except ValueError:
#         ...

#     print(f"Hello, selected AssemblyStep: [bold magenta]{step.name}[/bold magenta]!")

#     failures = session.query(Failure).filter_by(assembly_step = step).all()


#     table = Table(title=f"Failures for assembly step {step.name}")
#     table.add_column("id", justify="left", style="cyan", no_wrap=True)
#     table.add_column("description", justify="left", style="cyan")
#     table.add_column("# instances", justify="right", style="green")



#     for f in failures:
#         num_f_instances = session.query(FailureInstance).filter_by(assembly_step = step, failure = f).count()

#         table.add_row(f"{f.id}", f.description, str(num_f_instances))
    
#     console = Console()
#     console.print(table)
#     session.close()


# @app.command()
# def list_imps(assembly_step: int):
#     session = data_controller.create_session()
#     try:
#         step = AssemblyStep(assembly_step)
#     except ValueError:
#         ...
#     print(f"Hello, selected AssemblyStep: [bold magenta]{step.name}[/bold magenta]!")

#     improvements = session.query(Improvement).filter_by(assembly_step = step).all()
    
#     table = Table(title=f"Improvements for assembly step {step.name}")
#     table.add_column("id", justify="left", style="cyan", no_wrap=True)
#     table.add_column("title", justify="left", style="cyan", max_width=15)
#     table.add_column("description", justify="left", style="cyan")
#     table.add_column("Cable disconnect", justify="right", style="green", max_width=5)
#     table.add_column("# instances", justify="right", style="green", max_width=5)


#     for i in improvements:
#         num_instances = session.query(ImprovementInstance).filter_by(assembly_step = step, improvement = i).count()

#         table.add_row(str(i.id),i.title, i.description, str(i.cable_must_disconnected), str(num_instances))
    
#     console = Console()
#     console.print(table)
#     session.close()


# @app.command()
# def list_imp_instances(step: int):
#     with data_controller.session_context() as session:
#         try:
#             step = AssemblyStep(step)
#         except ValueError:
#             print(f"[bold red]There is no assembly step with value = {step}![/bold red]")
#             return

#         imps = session.query(Improvement).filter_by(assembly_step = step).all()

#         imp_instances = {instance for imp in imps for instance in session.query(ImprovementInstance).filter_by(improvement = imp).all() }

#         print(f"instances found: {len(imp_instances)}")
        
        
#         # table = Table(title=f"FailureInstance for failure: {fail}")
#         # table.add_column("id", justify="left", style="cyan", no_wrap=True)
#         # table.add_column("AssemblyStep", justify="left", style="cyan")
#         # table.add_column("Measurement-id", justify="right", style="green", max_width=5)

#         # for fi in fail_instances:
#         #     table.add_row(str(fi.id), str(fi.assembly_step.name), str(fi.measurement.id))

#         # console = Console()
#         # console.print(table)
#         # session.close()
    




    
    
    




if __name__ == "__main__":
    app()
