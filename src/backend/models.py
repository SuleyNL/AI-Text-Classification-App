from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Person(Base):
    """
    Represents a person in the database.

    Attributes:
        person_id (int): Unique identifier for the person.
        person_name (str): Name of the person.
        person_birthdate (datetime): Birthdate of the person.
        docs (List[PersonDoc]): List of documents associated with the person.
    """
    __tablename__ = 'persons'
    person_id = Column(Integer, primary_key=True)
    person_name = Column(String)
    person_birthdate = Column(DateTime)
    docs = relationship('PersonDoc', back_populates='person')


class PersonDoc(Base):
    """
    Represents the association between a person and a document.

    Attributes:
        person_id (int): ID of the associated person.
        doc_id (str): ID of the associated document.
        person (Person): The associated Person object.
        doc (Doc): The associated Doc object.
    """
    __tablename__ = 'persons_docs'
    person_id = Column(Integer, ForeignKey('persons.person_id'), primary_key=True)
    doc_id = Column(String, ForeignKey('docs.doc_id'), primary_key=True)
    person = relationship('Person', back_populates='docs')
    doc = relationship('Doc', back_populates='persons')


class Doc(Base):
    """
    Represents a document in the database.

    Attributes:
        doc_id (str): Unique identifier for the document.
        doc_path (str): Path to the document file.
        doc_text_path (str): Path to the extracted text of the document.
        doc_text_html (str): HTML representation of the document text.
        doc_name (str): Name of the document.
        created_at (datetime): Timestamp of document creation.
        persons (List[PersonDoc]): List of persons associated with the document.
        labels (List[Label]): List of labels associated with the document.
    """
    __tablename__ = 'docs'
    doc_id = Column(String, primary_key=True)
    doc_path = Column(String, unique=True)
    doc_text_path = Column(String)
    doc_text_html = Column(String)
    doc_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    persons = relationship('PersonDoc', back_populates='doc')
    labels = relationship('Label', back_populates='doc')


class Label(Base):
    """
    Represents a label applied to a document.

    Attributes:
        doc_id (str): ID of the associated document.
        label_id (int): Unique identifier for the label.
        start_char (int): Starting character position of the label in the document.
        end_char (int): Ending character position of the label in the document.
        label_content (str): Content of the label.
        label_category_id (int): ID of the associated label category.
        doc (Doc): The associated Doc object.
        category (LabelCategory): The associated LabelCategory object.
    """
    __tablename__ = 'labels'
    doc_id = Column(String, ForeignKey('docs.doc_id'))
    label_id = Column(Integer, primary_key=True)
    start_char = Column(Integer)
    end_char = Column(Integer)
    label_content = Column(String)
    label_category_id = Column(Integer, ForeignKey('label_categories.label_category_id'))
    doc = relationship('Doc', back_populates='labels')
    category = relationship('LabelCategory', back_populates='labels')


class LabelCategory(Base):
    """
    Represents a category for labels.

    Attributes:
        label_category_id (int): Unique identifier for the label category.
        label_category_name (str): Name of the label category.
        labels (List[Label]): List of labels associated with this category.
    """
    __tablename__ = 'label_categories'
    label_category_id = Column(Integer, primary_key=True)
    label_category_name = Column(String)
    labels = relationship('Label', back_populates='category')
