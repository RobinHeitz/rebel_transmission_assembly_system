# %%

from numpy import delete
import sqlalchemy as db

from data_management.model import Transmission, TransmissionConfiguration
from data_management.model import Measurement, Assembly, AssemblyStep


from sqlalchemy.orm import sessionmaker




engine = db.create_engine('sqlite:///rebel.sqlite')
connection = engine.connect()
metadata = db.MetaData()
session = sessionmaker(bind = engine)()

# %%

new_transmission = Transmission(
    transmission_configuration = TransmissionConfiguration.config_105_break_encoder,
)

session.add(new_transmission)
session.commit()


    # author = db.Table('Author', metadata, autoload=True, autoload_with=engine)
    # print(author.columns.keys())


    # # Session = sessionmaker(bind = engine)
    # # session = Session()

    # book = db.Table('book', metadata, autoload=True, autoload_with=engine)
    # print(book.columns.keys())


# %%

assembly = Assembly(assembly_step = AssemblyStep.step_1_no_flexring, transmission = new_transmission)

session.add(assembly)
session.commit()

# %%
measurement = Measurement(title="Test", assembly = assembly)
session.add(measurement)
session.commit()


# %%


get_trans = db.Table("Transmission", metadata, autoload=True, autoload_with=engine)
print(get_trans.columns.keys())
