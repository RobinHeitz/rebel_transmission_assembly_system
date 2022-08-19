from sqlalchemy import Column, Integer, String, ForeignKey, Table, Enum, DateTime
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
import enum
from datetime import datetime


class TransmissionConfiguration(enum.Enum):
    config_80 = 1
    config_80_encoder = 2

    config_105 = 3
    config_105_break = 4
    config_105_encoder = 5
    config_105_break_encoder = 6


class AssemblyStep(enum.Enum):
    step_1_no_flexring = 1
    step_2_with_flexring = 2
    step_3_gearoutput_not_screwed = 3
    step_4_gearoutput_screwed = 4

Base = declarative_base()

class Transmission(Base):
    __tablename__ = "transmission"
    transmission_id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    transmission_configuration = Column(Enum(TransmissionConfiguration))
    
    finished_date = Column(DateTime)
    assemblies = relationship("Assembly", backref=backref("transmission"))


class Assembly(Base):
    __tablename__ = "assembly"
    assembly_id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now)

    assembly_step = Column(Enum(AssemblyStep))
    transmission_id = Column(Integer, ForeignKey("transmission.transmission_id"))
    
    measurements = relationship("Measurement", backref=backref("assembly"))


class Measurement(Base):
    __tablename__ = "measurement"
    measurement_id = Column(Integer, primary_key=True)
    title = Column(String)
    assembly_id = Column(Integer, ForeignKey("assembly.assembly_id"))




# class AssemblyStep(Base):
#     ...
#     # Beschreibung
#     # id
#     # Bild??

# class ErrorDescription(Base):
#     ...






# author_publisher = Table(
#     "author_publisher",
#     Base.metadata,
#     Column("author_id", Integer, ForeignKey("author.author_id")),
#     Column("publisher_id", Integer, ForeignKey("publisher.publisher_id")),
# )

# book_publisher = Table(
#     "book_publisher",
#     Base.metadata,
#     Column("book_id", Integer, ForeignKey("book.book_id")),
#     Column("publisher_id", Integer, ForeignKey("publisher.publisher_id")),
# )

# class Author(Base):
#     __tablename__ = "author"
#     author_id = Column(Integer, primary_key=True)
#     first_name = Column(String)
#     last_name = Column(String)
#     books = relationship("Book", backref=backref("author"))
#     publishers = relationship(
#         "Publisher", secondary=author_publisher, back_populates="authors"
#     )

#     def __str__(self):
#         return f"Author's name: {self.first_name} {self.last_name}"

# class Book(Base):
#     __tablename__ = "book"
#     book_id = Column(Integer, primary_key=True)
#     author_id = Column(Integer, ForeignKey("author.author_id"))
#     title = Column(String)
#     publishers = relationship(
#         "Publisher", secondary=book_publisher, back_populates="books"
#     )

#     def __str__(self) -> str:
#         return f"Book: book_id = {self.book_id} / author_id = {self.author_id} / title = {self.title}"

# class Publisher(Base):
#     __tablename__ = "publisher"
#     publisher_id = Column(Integer, primary_key=True)
#     name = Column(String)
#     authors = relationship(
#         "Author", secondary=author_publisher, back_populates="publishers"
#     )
#     books = relationship(
#         "Book", secondary=book_publisher, back_populates="publishers"
#     )

# class MyNewTable(Base):
#     __tablename__ = "mynewtable"
#     my_id = Column(Integer, primary_key=True)
#     my_text = Column(String)