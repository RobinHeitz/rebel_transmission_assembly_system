# %%
from ensurepip import version
import os, shutil

from pathlib import Path

alembic_versions =  Path(__file__).parent.joinpath("alembic").joinpath("versions").glob("**/*")
db = Path(__file__).parent.joinpath("rebel.sqlite")

if db.exists():
    os.remove(str(db))



versions = [f for f in alembic_versions if f.is_file()]

for file in versions:
    os.remove(file)





