import json
import os
import uuid
from typing import List, Dict, Tuple
from urllib.parse import parse_qsl

from bs4 import BeautifulSoup
from flask import Flask, jsonify, request, Response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from src.AIServiceLogic import SentenceEmbedder, AI_solution, MultiClassifier

from .models import Base, Person, PersonDoc, Doc, LabelCategory
from flask_cors import CORS

"""
AI-Powered Document Analysis and Categorization API

This Flask-based API provides endpoints for managing persons, documents, and AI-powered
document analysis. It uses SQLAlchemy for database operations and integrates with an
AI service for document processing and categorization.

The API allows users to:
1. Create and retrieve person information
2. Upload documents associated with persons
3. Retrieve documents and their AI-processed content
4. Manage label categories for document overview
5. Retrieve categorized snippets from documents
"""

# Initialize AI solution
solution: AI_solution = SentenceEmbedder()
#solution: AI_solution = MultiClassifier()
#r = solution.classification_strategy\
#    .get_labels('I get happy if one day I will see the world and eat food from every country and meet new people')
#print(r)

# Database configuration
database_file: str = 'sqlite:///database.db'
if not os.path.exists('database.db'):
    open('database.db', 'a').close()

# Create a local SQLite database
engine = create_engine(database_file, echo=True)

# Create the tables in the database
Base.metadata.create_all(engine)

# Create a session factory
SessionLocal = sessionmaker(bind=engine)

# Flask app
app = Flask(__name__)

# Allow CORS for the specific origin
CORS(app, resources={r"/*": {"origins": "http://localhost:4200"}})


def get_db() -> Session:
    """
    Creates and returns a new database session.

    Returns:
        Session: A new SQLAlchemy database session.

    Raises:
        Exception: If there's an error creating the session.
    """
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        print(e)
        db.close()


@app.route('/', methods=['GET', 'POST', 'PUT', 'PATCH'])
def read_root() -> Tuple[Response, int]:
    """
    Root endpoint for the API.

    Returns:
        Tuple[Response, int]: A JSON response with a welcome message and HTTP status code 200.
    """
    return jsonify({"message": "Welcome to the AI-Text Highlighting API"}), 200


# Persons
@app.route('/persons', methods=['POST'])
def create_person() -> Tuple[Response, int]:
    """
    Creates a new person in the database.

    Expects JSON input with 'person_name' and 'person_birthdate'.

    Returns:
        Tuple[Response, int]: A JSON response with the created person's details and HTTP status code.

    Example response:
        ({
            "person_id": 1,
            "person_name": "John Doe",
            "person_birthdate": "1990-01-01T00:00:00",
            "docs": []
        }, 201)
    """
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
            "person_birthdate": new_person.person_birthdate.isoformat()
        }), 201

    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
        return jsonify({"error": "Person Creation failed"}), 500
    finally:
        db.close()


@app.route('/persons/<int:person_id>', methods=['GET'])
def get_person(person_id: int) -> Tuple[Response, int]:
    """
    Retrieves information about a specific person and their associated documents.

    Args:
        person_id (int): The ID of the person to retrieve.

    Returns:
        Tuple[Response, int]: A JSON response with the person's details and associated documents,
                              and HTTP status code.

    Example response:
        ({
            "person_id": 1,
            "person_name": "John Doe",
            "person_birthdate": "1990-01-01T00:00:00",
            "docs": [
                {
                    "doc_id": "abc123",
                    "doc_name": "Resume.pdf",
                    "doc_path": "/uploads/Resume.pdf",
                    "created_at": "2023-07-04T12:00:00"
                }
            ]
        }, 200)
    """
    db = get_db()
    person = db.query(Person).filter(Person.person_id == person_id).first()
    if person is None:
        return jsonify({"error": "Person not found"}), 404

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
    }), 200


@app.route('/persons', methods=['GET'])
def get_persons() -> Tuple[Response, int]:
    """
    Retrieves a list of all persons in the database.

    Returns:
        Tuple[Response, int]: A JSON response with a list of all persons and HTTP status code.

    Example response:
        ({
            "persons": [
                {
                    "person_id": 1,
                    "person_name": "John Doe",
                    "person_birthdate": "1990-01-01T00:00:00"
                },
                {
                    "person_id": 2,
                    "person_name": "Jane Smith",
                    "person_birthdate": "1985-05-15T00:00:00"
                }
            ]
        }, 200)
    """
    db = get_db()
    persons = db.query(Person).all()
    return jsonify([{
        "person_id": p.person_id,
        "person_name": p.person_name,
        "person_birthdate": p.person_birthdate.isoformat() if p.person_birthdate else None
    } for p in persons]), 200


@app.route('/persons/<int:person_id>/docs', methods=['POST'])
def create_document_for_person(person_id: int) -> Tuple[Response, int]:
    """
    Creates a new document associated with a specific person.

    Args:
        person_id (int): The ID of the person to associate the document with.

    Returns:
        Tuple[Response, int]: A JSON response with the created document's details and HTTP status code.

    Example response:
        ({
            "doc_id": "abc123",
            "doc_name": "Resume.pdf",
            "created_at": "2023-07-04T12:00:00",
            "person_id": 1
        }, 201)
    """
    try:
        db = get_db()

        person = db.query(Person).filter(Person.person_id == person_id).first()
        if person is None:
            return jsonify({"error": "Person not found"}), 404

        if not request.data:
            return jsonify({"error": "Missing file data"}), 400

        query_string = request.query_string.decode('utf-8')
        query_params = dict(parse_qsl(query_string))

        doc_name = query_params.get('doc_name')
        doc_path = query_params.get('doc_path')
        if not doc_name:
            doc_name = f"temp_pdf_{str(uuid.uuid4())}.pdf"

        filepath = os.path.join(os.getcwd(), "uploads", doc_name)

        doc_text_html = solution.ingest_document(filepath=filepath, filename=doc_name, person_id=person_id, request_data=request.data)
        assert isinstance(doc_text_html, str), f"Expected string, got {type(doc_text_html)}"

        new_doc = Doc(
            doc_id=str(uuid.uuid4()),
            doc_path=doc_path,
            doc_text_path='abc',
            doc_text_html=doc_text_html,
            doc_name=doc_name,
            created_at=datetime.utcnow()
        )

        db.add(new_doc)

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
def get_docs() -> Tuple[Response, int]:
    """
    Retrieves a list of all documents in the database.

    Returns:
        Tuple[Response, int]: A JSON response with a list of all documents and HTTP status code.

    Example response:
        ({
            "docs": [
                {
                    "doc_id": "abc123",
                    "doc_name": "Resume.pdf",
                    "created_at": "2023-07-04T12:00:00",
                    "doc_text_html": "<html>...</html>"
                },
                {
                    "doc_id": "def456",
                    "doc_name": "Cover_Letter.pdf",
                    "created_at": "2023-07-05T14:30:00",
                    "doc_text_html": "<html>...</html>"
                }
            ]
        }, 200)
    """
    db = get_db()
    docs = db.query(Doc).all()
    return jsonify([{
        "doc_id": d.doc_id,
        "doc_name": d.doc_name,
        "created_at": d.created_at.isoformat() if d.created_at else None,
        "doc_text_html": d.doc_text_html
    } for d in docs]), 200


@app.route('/docs/<string:doc_id>', methods=['GET'])
def get_doc(doc_id: str) -> Tuple[Response, int]:
    """
    Retrieves information about a specific document.

    Args:
        doc_id (str): The ID of the document to retrieve.

    Returns:
        Tuple[Response, int]: A JSON response with the document's details and HTTP status code.

    Example response:
        ({
            "id": "abc123",
            "name": "Resume.pdf",
            "category": ["Work Experience", "Education"],
            "html": "<html>...</html>",
            "created_at": "2023-07-04T12:00:00"
        }, 200)
    """
    db = get_db()
    doc = db.query(Doc).filter(Doc.doc_id == doc_id).first()
    if doc is None:
        return jsonify({"error": "Document not found"}), 404
    return jsonify({
        "id": doc.doc_id,
        "name": doc.doc_name,
        "category": solution.extract_unique_categories(doc.doc_text_html),
        "html": doc.doc_text_html,
        "created_at": doc.created_at.isoformat() if doc.created_at else None,
    }), 200


@app.route('/persons/<int:person_id>/docs', methods=['GET'])
def get_person_docs(person_id: int) -> Tuple[Response, int]:
    """
    Retrieves all documents associated with a specific person.

    Args:
        person_id (int): The ID of the person whose documents to retrieve.

    Returns:
        Tuple[Response, int]: A JSON response with a list of the person's documents and HTTP status code.

    Example response:
        ({
            "docs": [
                {
                    "doc_id": "abc123",
                    "doc_name": "Resume.pdf",
                    "created_at": "2023-07-04T12:00:00",
                    "doc_text_html": "<html>...</html>"
                },
                {
                    "doc_id": "def456",
                    "doc_name": "Cover_Letter.pdf",
                    "created_at": "2023-07-05T14:30:00",
                    "doc_text_html": "<html>...</html>"
                }
            ]
        }, 200)
    """
    db = get_db()
    person = db.query(Person).filter(Person.person_id == person_id).first()
    if person is None:
        return jsonify({"error": "Person not found"}), 404
    return jsonify([{
        "doc_id": d.doc.doc_id,
        "doc_name": d.doc.doc_name,
        "created_at": d.doc.created_at.isoformat() if d.doc.created_at else None,
        "doc_text_html": d.doc.doc_text_html
    } for d in person.docs]), 200


@app.route('/label_categories', methods=['POST'])
def create_label_category() -> Tuple[Response, int]:
    """
    Creates a new label category.

    Expects JSON input with 'label_category_name' and 'label_category_id'.

    Returns:
        Tuple[Response, int]: A JSON response with the created category's details and HTTP status code.

    Example response:
        ({
            "label_category_id": 1,
            "label_category_name": "Work Experience"
        }, 201)
    """
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
def get_label_categories() -> Tuple[Response, int]:
    """
    Retrieves all label categories.

    Returns:
        Tuple[Response, int]: A JSON response with a list of all label categories and HTTP status code.

    Example response:
        ({
            "categories": [
                {
                    "label_category_id": 1,
                    "label_category_name": "Work Experience"
                },
                {
                    "label_category_id": 2,
                    "label_category_name": "Education"
                }
            ]
        }, 200)
    """
    db = get_db()
    label_categories = db.query(LabelCategory).all()
    return jsonify([{
        "label_category_id": lc.label_category_id,
        "label_category_name": lc.label_category_name
    } for lc in label_categories]), 200


@app.route('/categories/<string:person_id>', methods=['GET'])
def get_categories_person(person_id: str) -> Tuple[Response, int]:
    """
    Retrieves all categories and their counts for documents associated with a specific person.

    Args:
        person_id (str): The ID of the person whose document categories to retrieve.

    Returns:
        Tuple[Response, int]: A JSON response with category information and HTTP status code.

    Example response:
        ({
            "categories": [
                {
                    "id": 1,
                    "name": "Work Experience",
                    "numberOfLinkedSnippets": 5
                },
                {
                    "id": 2,
                    "name": "Education",
                    "numberOfLinkedSnippets": 3
                }
            ]
        }, 200)
    """

    def count_categories(html_string: str) -> Dict[int, int]:
        soup = BeautifulSoup(html_string, 'html.parser')
        category_counts = {}
        spans = soup.find_all('span')
        for span in spans:
            if 'class' in span.attrs:
                classes = span.attrs['class']
                for cls in classes:
                    if cls.startswith('cat') and cls[3:].isdigit():
                        print('cls: ' + cls)
                        category_id = int(cls[3:])
                        if category_id != '':
                            if category_id in category_counts:
                                category_counts[category_id] += 1
                            else:
                                category_counts[category_id] = 1
        return category_counts

    db = get_db()
    person = db.query(Person).filter(Person.person_id == person_id).first()

    if person is None:
        return jsonify({"error": "Person not found"}), 404

    category_counts = {}

    associated_docs = db.query(Doc).join(PersonDoc).filter(PersonDoc.person_id == person_id).all()

    for doc in associated_docs:
        doc_category_counts = count_categories(doc.doc_text_html)
        for category, count in doc_category_counts.items():
            if category in category_counts:
                category_counts[category] += count
            else:
                category_counts[category] = count

    result = []
    for category_id, count in category_counts.items():
        result.append({
            "id": category_id,
            "name": solution.categories[category_id - 1]["name"],
            "numberOfLinkedSnippets": count
        })
    return jsonify(result), 200


@app.route('/categories/<int:person_id>/<int:category_id>', methods=['GET'])
def get_snippets_person(person_id: int, category_id: int) -> Tuple[Response, int]:
    """
    Retrieves snippets from documents associated with a specific person and category.

    Args:
        person_id (int): The ID of the person whose snippets to retrieve.
        category_id (int): The ID of the category to filter snippets.

    Returns:
        Tuple[Response, int]: A JSON response with snippet information and HTTP status code.

    Example response:
        ({
            "category": 1,
            "snippets": [
                {
                    "document_id": "abc123",
                    "document_name": "Resume.pdf",
                    "html": "<span class='cat1'>...</span>"
                },
                {
                    "document_id": "def456",
                    "document_name": "Cover_Letter.pdf",
                    "html": "<span class='cat1'>...</span>"
                }
            ]
        }, 200)
    """

    def extract_relevant_snippets(html_string: str, category_id: int) -> List[str]:
        soup = BeautifulSoup(html_string, 'html.parser')
        spans = soup.find_all('span')
        snippets = []

        for i, span in enumerate(spans):
            if 'class' in span.attrs:
                classes = span.attrs['class']
                if f'cat{category_id}' in classes:
                    snippet = ""
                    if i > 0:
                        snippet += str(spans[i - 1])
                    snippet += str(span)
                    if i < len(spans) - 1:
                        snippet += str(spans[i + 1])
                    snippets.append(snippet)

        return snippets

    db = get_db()
    person = db.query(Person).filter(Person.person_id == person_id).first()

    if person is None:
        return jsonify({"error": "Person not found"}), 404

    snippets = []

    associated_docs = db.query(Doc).join(PersonDoc).filter(PersonDoc.person_id == person_id).all()

    for doc in associated_docs:
        relevant_snippets = extract_relevant_snippets(doc.doc_text_html, category_id)
        for snippet in relevant_snippets:
            snippets.append({
                "document_id": doc.doc_id,
                "document_name": doc.doc_name,
                "html": snippet
            })

    result = {
        "category": category_id,
        "snippets": snippets
    }

    return jsonify(result), 200


def create_label_categories() -> None:
    """
    Creates or updates label categories from a JSON file.

    This function reads category data from a 'Categories.json' file and creates
    or updates corresponding LabelCategory entries in the database.
    """
    session = SessionLocal()

    # Get the directory of the current script
    script_dir = os.path.dirname(__file__)
    # Construct the path to Categories.json
    categories_path = os.path.join(script_dir, '../Categories.json')

    with open(categories_path, 'r') as file:
        categories_data = json.load(file)

    categories = categories_data.get('categories', [])

    try:
        for category in categories:
            existing_category = session.query(LabelCategory).filter_by(label_category_id=category['id']).first()

            if existing_category:
                existing_category.label_category_name = category['name']
                print(f"Updated category: {category['name']}")
            else:
                new_category = LabelCategory(
                    label_category_id=category['id'],
                    label_category_name=category['name']
                )
                session.add(new_category)
                print(f"Created new category: {category['name']}")

        session.commit()
        print("All categories have been successfully created or updated.")

    except Exception as e:
        session.rollback()
        print(f"An unexpected error occurred: {str(e)}")

    finally:
        session.close()


# Initialize label categories
create_label_categories()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8001, debug=True)
