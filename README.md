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

## License

This project is licensed under the MIT License - see the LICENSE.md file for details.