# %%
import yaml
from pathlib import Path

def load_config():

    p = Path(__file__).parent.joinpath("current_limits.yaml")

    try:
        with open(str(p), "r") as stream:
            loaded_config = yaml.safe_load(stream)

            return loaded_config["limits"]

    except Exception as e:
        print(e)


if __name__ == "__main__":
    print(load_config())
