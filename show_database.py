from data_management import data_controller
from data_management.model import AssemblyStep, Failure, FailureInstance, Improvement, ImprovementInstance
from rich import print
from rich.table import Table
from rich.console import Console




import typer

app = typer.Typer()




@app.command()
def list_fails(assembly_step: int):
    session = data_controller.create_session()
    
    try:
        step = AssemblyStep(assembly_step)
    except ValueError:
        ...

    print(f"Hello, selected AssemblyStep: [bold magenta]{step.name}[/bold magenta]!")

    failures = session.query(Failure).filter_by(assembly_step = step).all()


    table = Table(title=f"Failures for assembly step {step.name}")
    table.add_column("id", justify="left", style="cyan", no_wrap=True)
    table.add_column("description", justify="left", style="cyan")
    table.add_column("# instances", justify="right", style="green")



    for f in failures:
        num_f_instances = session.query(FailureInstance).filter_by(assembly_step = step, failure = f).count()

        table.add_row(f"{f.id}", f.description, str(num_f_instances))
    
    console = Console()
    console.print(table)
    session.close()


@app.command()
def list_imps(assembly_step: int):
    session = data_controller.create_session()
    try:
        step = AssemblyStep(assembly_step)
    except ValueError:
        ...
    print(f"Hello, selected AssemblyStep: [bold magenta]{step.name}[/bold magenta]!")

    improvements = session.query(Improvement).filter_by(assembly_step = step).all()
    
    table = Table(title=f"Improvements for assembly step {step.name}")
    table.add_column("id", justify="left", style="cyan", no_wrap=True)
    table.add_column("title", justify="left", style="cyan", max_width=15)
    table.add_column("description", justify="left", style="cyan")
    table.add_column("Cable disconnect", justify="right", style="green", max_width=5)
    table.add_column("# instances", justify="right", style="green", max_width=5)


    for i in improvements:
        num_instances = session.query(ImprovementInstance).filter_by(assembly_step = step, improvement = i).count()

        table.add_row(str(i.id),i.title, i.description, str(i.cable_must_disconnected), str(num_instances))
    
    console = Console()
    console.print(table)
    session.close()


@app.command()
def list_imp_instances(step: int):
    with data_controller.session_context() as session:
        try:
            step = AssemblyStep(step)
        except ValueError:
            print(f"[bold red]There is no assembly step with value = {step}![/bold red]")
            return

        imps = session.query(Improvement).filter_by(assembly_step = step).all()

        imp_instances = {instance for imp in imps for instance in session.query(ImprovementInstance).filter_by(improvement = imp).all() }

        print(f"instances found: {len(imp_instances)}")
        
        
        # table = Table(title=f"FailureInstance for failure: {fail}")
        # table.add_column("id", justify="left", style="cyan", no_wrap=True)
        # table.add_column("AssemblyStep", justify="left", style="cyan")
        # table.add_column("Measurement-id", justify="right", style="green", max_width=5)

        # for fi in fail_instances:
        #     table.add_row(str(fi.id), str(fi.assembly_step.name), str(fi.measurement.id))

        # console = Console()
        # console.print(table)
        # session.close()
    




    
    
    




if __name__ == "__main__":
    app()
