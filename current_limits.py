# %%
import yaml
from pathlib import Path
import traceback

from data_management.model import AssemblyStep

config = None

def load_config():

    p = Path(__file__).parent.joinpath("current_limits.yaml")

    try:
        with open(str(p), "r") as stream:
            loaded_config = yaml.safe_load(stream)

            return loaded_config["limits"]

    except Exception as e:
        print(e)


def get_current_limit_for_assembly_step(step:AssemblyStep):
    global config
    if config == None:
        config = load_config()
    
    try:
        limit_current = config[step.name]
    except KeyError:
        print("ERROR Occured! Can't read current-limit for given assemblyStep: ", step)
        print(config)
        print(traceback.traceback.format_exception())
        limit_current = 123
    finally:
        return limit_current
        


if __name__ == "__main__":

    print( get_current_limit_for_assembly_step(AssemblyStep.step_2_with_flexring))
