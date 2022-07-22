# %%

from numpy import delete
import sqlalchemy as db

from data_management.model import Author, Book, Publisher

from sqlalchemy.orm import sessionmaker



if __name__ == "__main__":
    ...

    engine = db.create_engine('sqlite:///rebel.sqlite')
    connection = engine.connect()
    metadata = db.MetaData()

    author = db.Table('Author', metadata, autoload=True, autoload_with=engine)
    print(author.columns.keys())


    # Session = sessionmaker(bind = engine)
    # session = Session()

    book = db.Table('book', metadata, autoload=True, autoload_with=engine)
    print(book.columns.keys())

    session = sessionmaker(bind = engine)()

# %%

    newBook = Book(title="My new book!")
    session.add(newBook)
    session.commit()

# %%

result = session.query(Book).all()
for b in result:
    print(b)

# %%

newAuthor = Author(first_name="Heinz", last_name="Peter",)
session.add(newAuthor)
session.commit()

# %%

authors = session.query(Author).all()
for a in authors:

    print(a.first_name)
    if a.first_name == "Robin":
        session.delete(a)

session.commit()

# %%

