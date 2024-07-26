# AI-Text-Classification-App
An app to classify text chunks from documents into pre-defined categories. Allowing the user to jump to the most relevant pieces of information without having to read the whole document.

## Overview
This project is a Flask-based API that provides document analysis and categorization functionality using AI techniques. It allows users to manage persons, upload documents, process them using AI, and retrieve categorized snippets based on predefined label categories.

## Features
- Person management (create, retrieve)
- Document upload and association with persons
- AI-powered document text-highlighting and sentence labeling
- Retrieval of categorized document snippets
- Label-category management

## Architecture

The application follows a modular architecture with the following main components:

1. Flask API (`app.py`)
2. Database models (`models.py`)
3. AI-Service Logic Modules:
   - `src/AIServiceLogic/MultiClassification`
   - `src/AIServiceLogic/SentenceEmbedding`


The following diagram provides an overview of the project's architecture:

![Project Overview](Documentation/ATCA_overview.png)


## AI Solutions

The application supports two AI solutions for document processing:

1. `MultiClassificationSolution`: Uses a classification strategy to categorize sentences.
2. `SentenceEmbeddingSolution`: Uses sentence embeddings and transformation strategies for categorization.

To switch between solutions, modify the initialization in `app.py`:

```python
solution: AI_solution = SentenceEmbedder()
# or
solution: AI_solution = MultiClassifier()
```


## Document Processing Flow

The sequence diagram below illustrates the flow of document processing in our application:

```mermaid
sequenceDiagram
    participant C as Client
    participant A as API (Flask)
    participant S as AI Solution
    participant D as Database

    C->>A: POST /persons/{person_id}/docs
    A->>D: Create new Doc entry
    A->>S: process_document(filepath, filename, person_id)
    S->>S: Extract text from PDF
    S->>S: Split text into sentences
    S->>S: Apply AI strategy (Classification or Embedding)
    S->>S: Generate HTML with categorized sentences
    S-->>A: Return processed HTML
    A->>D: Update Doc with processed HTML
    A-->>C: Return document details
```

## Database Schema

Our application uses the following database schema:

```sql
CREATE TABLE Person (
    person_id INTEGER PRIMARY KEY,
    person_name TEXT NOT NULL,
    person_birthdate DATE
);

CREATE TABLE Doc (
    doc_id TEXT PRIMARY KEY,
    doc_name TEXT NOT NULL,
    doc_path TEXT NOT NULL,
    doc_text_path TEXT,
    doc_text_html TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE PersonDoc (
    person_id INTEGER,
    doc_id TEXT,
    PRIMARY KEY (person_id, doc_id),
    FOREIGN KEY (person_id) REFERENCES Person(person_id),
    FOREIGN KEY (doc_id) REFERENCES Doc(doc_id)
);

CREATE TABLE LabelCategory (
    label_category_id INTEGER PRIMARY KEY,
    label_category_name TEXT NOT NULL
);
```

### Models

Our database models are defined in `models.py`.
For the complete implementation of these models, please refer to the `models.py` file in the repository.

## Setup and Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up the database:
   ```
   python -c "from app import db; db.create_all()"
   ```

4. Run the application:
   ```
   python app.py
   ```

## API Endpoints

- `/persons`: POST, GET
- `/persons/<int:person_id>`: GET
- `/persons/<int:person_id>/docs`: POST, GET
- `/docs`: GET
- `/docs/<string:doc_id>`: GET
- `/label_categories`: POST, GET
- `/categories/<string:person_id>`: GET
- `/categories/<int:person_id>/<int:category_id>`: GET

For detailed API documentation, please refer to the inline comments in `app.py`.

## Contributing

We welcome contributions to expand and improve this project. Here are some areas where you can contribute:

1. Implementing new AI solutions
2. Creating new transformation strategies for the `SentenceEmbeddingSolution`
3. Developing new classification strategies for the `MultiClassificationSolution`
4. Improving the existing embedding functions
5. Enhancing documentation and test coverage

Please see our [CONTRIBUTING.md](CONTRIBUTING.md) file for more details on how to contribute.

## License
This project is licensed under the MIT License - see the LICENSE.md file for details.