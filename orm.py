# %%

import sqlalchemy as db



if __name__ == "__main__":
    ...

    engine = db.create_engine('sqlite:///rebel.sqlite')
    connection = engine.connect()
    metadata = db.MetaData()

    census = db.Table('Author', metadata, autoload=True, autoload_with=engine)
    print(census.columns.keys())
