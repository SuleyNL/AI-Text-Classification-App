import json
import os
import uuid
from urllib.parse import parse_qsl

from flask import Flask, jsonify, request
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from src.AIService import SentenceEmbedder, AI_solution

# One of the multiple options for an AIsolution!
solution: AI_solution = SentenceEmbedder()

database_file = 'sqlite:///database.db'
if not os.path.exists('database.db'):
    open('database.db', 'a').close()

# Create a SQLite database
engine = create_engine(database_file, echo=True)

Base = declarative_base()


# Define the models
class Person(Base):
    __tablename__ = 'persons'
    person_id = Column(Integer, primary_key=True)
    person_name = Column(String)
    person_birthdate = Column(DateTime)
    docs = relationship('PersonDoc', back_populates='person')


class PersonDoc(Base):
    __tablename__ = 'persons_docs'
    person_id = Column(Integer, ForeignKey('persons.person_id'), primary_key=True)
    doc_id = Column(String, ForeignKey('docs.doc_id'), primary_key=True)
    person = relationship('Person', back_populates='docs')
    doc = relationship('Doc', back_populates='persons')


class Doc(Base):
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
    __tablename__ = 'label_categories'
    label_category_id = Column(Integer, primary_key=True)
    label_category_name = Column(String)
    labels = relationship('Label', back_populates='category')


# Create the tables in the database
Base.metadata.create_all(engine)

# Create a session factory
SessionLocal = sessionmaker(bind=engine)

# Flask app
app = Flask(__name__)


# Helper function to get database session
def get_db():
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        print(e)
        db.close()


# Routes
@app.route('/', methods=['GET', 'POST', 'PUT', 'PATCH'])
def read_root():
    return jsonify({"message": "Welcome to the API"})


# PERSON
@app.route('/persons', methods=['POST'])
def create_person():
    try:
        db = get_db()
        data = request.json

        new_person = Person(
            person_name=data['person_name'],
            person_birthdate=datetime.fromisoformat(data['person_birthdate'])
        )

        db.add(new_person)
        db.commit()

        return jsonify({
            "person_id": new_person.person_id,
            "person_name": new_person.person_name,
            "person_birthdate": new_person.person_birthdate.isoformat(),
            "docs": new_person.docs
        }), 201

    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
        return jsonify({"error": "Person Creation failed"}), 500
    finally:
        db.close()


@app.route('/persons/<int:person_id>', methods=['GET'])
def get_person(person_id):
    db = get_db()
    person = db.query(Person).filter(Person.person_id == person_id).first()
    if person is None:
        return jsonify({"error": "Person not found"}), 404

    # Fetch associated documents through the PersonDoc association
    associated_docs = db.query(Doc).join(PersonDoc).filter(PersonDoc.person_id == person_id).all()

    return jsonify({
        "person_id": person.person_id,
        "person_name": person.person_name,
        "person_birthdate": person.person_birthdate.isoformat() if person.person_birthdate else None,
        "docs": [{
            "doc_id": doc.doc_id,
            "doc_name": doc.doc_name,
            "doc_path": doc.doc_path,
            "created_at": doc.created_at.isoformat() if doc.created_at else None
        } for doc in associated_docs]
    })


@app.route('/persons', methods=['GET'])
def get_persons():
    db = get_db()
    persons = db.query(Person).all()
    return jsonify([{
        "person_id": p.person_id,
        "person_name": p.person_name,
        "person_birthdate": p.person_birthdate.isoformat() if p.person_birthdate else None
    } for p in persons])


# DOCUMENTS
@app.route('/persons/<int:person_id>/docs', methods=['POST'])
def create_document_for_person(person_id):
    try:
        db = get_db()

        # Check if the person exists
        person = db.query(Person).filter(Person.person_id == person_id).first()
        if person is None:
            return jsonify({"error": "Person not found"}), 404

        if not request.data:
            return jsonify({"error": "Missing file data"}), 400

        # Parse query string
        query_string = request.query_string.decode('utf-8')
        query_params = dict(parse_qsl(query_string))

        # Extract filename from query params
        doc_name = query_params.get('doc_name')
        doc_path = query_params.get('doc_path')
        if not doc_name:
            filename = f"temp_pdf_{str(uuid.uuid4())}.pdf"  # TODO: TEMPORARY FIX WHILE DEVELOPING, should return error 400
            # return jsonify({"error": "Missing filename"}), 400

        filepath = os.path.join(os.getcwd(), "uploads", doc_name)

        # AI LOGIC BELOW
        doc_text_html = solution.ingest_document(filepath, doc_name, person_id, request.data)
        assert isinstance(doc_text_html, str), f"Expected string, got {type(doc_text_html)}"

        # Create new document
        new_doc = Doc(
            doc_id=str(uuid.uuid4()),
            doc_path=doc_path,
            doc_text_path='abc',
            doc_text_html=doc_text_html,
            doc_name=doc_name,
            created_at=datetime.utcnow()
        )

        db.add(new_doc)

        # Create association between person and document
        person_doc = PersonDoc(
            person_id=person_id,
            doc_id=new_doc.doc_id
        )

        db.add(person_doc)
        db.commit()

        return jsonify({
            "doc_id": new_doc.doc_id,
            "doc_name": new_doc.doc_name,
            "created_at": new_doc.created_at.isoformat(),
            "person_id": person_id
        }), 201

    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
        return jsonify({"error": "File upload failed"}), 500
    finally:
        db.close()


@app.route('/docs', methods=['GET'])
def get_docs():
    db = get_db()
    docs = db.query(Doc).all()
    return jsonify([{
        "doc_id": d.doc_id,
        "doc_name": d.doc_name,
        "created_at": d.created_at.isoformat() if d.created_at else None,
        "doc_text_html": d.doc_text_html
    } for d in docs])


@app.route('/docs/<string:doc_id>', methods=['GET'])
def get_doc(doc_id):
    db = get_db()
    doc = db.query(Doc).filter(Doc.doc_id == doc_id).first()
    if doc is None:
        return jsonify({"error": "Document not found"}), 404
    return jsonify({
        "doc_id": doc.doc_id,
        "doc_name": doc.doc_name,
        "created_at": doc.created_at.isoformat() if doc.created_at else None,
        "doc_text_html": doc.doc_text_html
    })


@app.route('/persons/<int:person_id>/docs/test', methods=['GET'])
def get_person_docs(person_id):
    db = get_db()
    person = db.query(Person).filter(Person.person_id == person_id).first()
    if person is None:
        return jsonify({"error": "Person not found"}), 404
    return jsonify([{
        "doc_id": d.doc.doc_id,
        "doc_name": d.doc.doc_name,
        "created_at": d.doc.created_at.isoformat() if d.doc.created_at else None,
        "doc_text_html": d.doc_text_html
    } for d in person.docs])


# LABEL_CATEGORIES
@app.route('/label_categories', methods=['POST'])
def create_label_category():
    try:
        db = get_db()
        data = request.json

        new_label_category = LabelCategory(
            label_category_name=data['label_category_name'],
            label_category_id=data['label_category_id']
        )

        db.add(new_label_category)
        db.commit()

        return jsonify({
            "label_category_id": new_label_category.label_category_id,
            "label_category_name": new_label_category.label_category_name
        }), 201

    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
        return jsonify({"error": "Category creation failed"}), 500

    finally:
        db.close()


@app.route('/label_categories', methods=['GET'])
def get_label_categories():
    db = get_db()
    label_categories = db.query(LabelCategory).all()
    return jsonify([{
        "label_category_id": lc.label_category_id,
        "label_category_name": lc.label_category_name
    } for lc in label_categories])


# LABELS
@app.route('/chah/<int:person_id>', methods=['GET'])
def get_chah(person_id):
    db = get_db()
    person = db.query(Person).filter(Person.person_id == person_id).first()
    if person is None:
        return jsonify({"error": "Person not found"}), 404
    return jsonify([{
        "doc_id": d.doc.doc_id,
        "doc_name": d.doc.doc_name,
        "created_at": d.doc.created_at.isoformat() if d.doc.created_at else None,
        "doc_text_html": d.doc_text_html
    } for d in person.docs])



def create_label_categories():
    # Create a new database session
    session = SessionLocal()

    with open('../Categories.json', 'r') as file:
        categories_data = json.load(file)

    # Get the list of categories
    categories = categories_data.get('categories', [])

    try:
        for category in categories:
            # Check if the category already exists
            existing_category = session.query(LabelCategory).filter_by(label_category_id=category['id']).first()

            if existing_category:
                # Update existing category
                existing_category.label_category_name = category['name']
                print(f"Updated category: {category['name']}")
            else:
                # Create new category
                new_category = LabelCategory(
                    label_category_id=category['id'],
                    label_category_name=category['name']
                )
                session.add(new_category)
                print(f"Created new category: {category['name']}")

        # Commit the changes
        session.commit()
        print("All categories have been successfully created or updated.")

    except Exception as e:
        # Roll back the changes if there's any other error
        session.rollback()
        print(f"An unexpected error occurred: {str(e)}")

    finally:
        # Close the session
        session.close()


create_label_categories()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8001, debug=True)
