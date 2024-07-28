## Extensibility

This project is designed to be easily extensible in several ways:

### 1. Adding New AI Solutions

New AI solutions can be added by implementing the `AISolution` interface. The solution must implement the `process_document()` function. Examples of existing solutions:

- `MultiClassificationSolution`
- `SentenceEmbeddingSolution`

### 2. Adding new TransformationStrategies for the SentenceEmbeddingSolution

The `SentenceEmbeddingSolution` uses a `TransformationStrategy` to process embeddings. Developers can add new transformation strategies by implementing the `TransformationStrategy` interface and its `get_labels()` function. Current strategies include:

- `NoTransformation`
- `ThemeTransformation`

### 3. Adding new ClassificationStrategies for the MultiClassificationSolution  

The `MultiClassificationSolution` can be extended by adding new `ClassificationStrategy` implementations. These must follow the `ClassificationStrategy` interface rules and implement the `get_labels()` function. Currently implemented:

- `ComprehendIt`

### 4. Adding new EmbeddingFunctions

The `SentenceEmbeddingSolution` uses an `EmbeddingFunction` which can be swapped out and customized to use different embedding techniques or models.
Current strategies include:
- ```python
   class Mxbai(EmbeddingFunction):
    """
    An embedding function that uses the mxbai-embed-large model from Ollama.
    """
  
- ```python
   class Baai(EmbeddingFunction):
    """
    An embedding function that uses the BAAI/bge-large-en-v1.5 model from huggingfaces' transformers.
    """
   ```

### 5. Adding new Model_theory
New ideas, knowledge and other snippets for inspiration are always welcome. 
Right now there are two files containing background/context information which inform how we do things, 
these can be found in [SentenceEmbedding Theory file](src/AIServiceLogic/SentenceEmbedding/Model_theory.md) and in the [Multiclassification Theory file](src/AIServiceLogic/MultiClassification/Model_theory.md)

### 6. Testing out new combinations of EmbeddingFunctions, TransformationStrategies or ClassificationStrategies
Already existing functions have not been exhaustively tested, and it would be greatly appreciated for someone to test and document the performance of various combinations of these modules. 
This includes both subjective measurements of the models accuracy and feasibility, aswell as factual measurements of execution time, or dataset-based benchmarking of the models and techniques.


## Setup and Installation

1. Clone the repository:
   ```
   git clone https://github.com/SuleyNL/AI-Text-Classification-App.git
   ```

2. Install python dependencies:
   ```
   pip install -r requirements.txt
   ```
   
3. Set up the backend:
   ```cmd
   python -m src.backend.app
   ```
   ```output
   All categories have been successfully created or updated.
   * Serving Flask app 'app'
   * Debug mode: on
   WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
   * Running on all addresses (0.0.0.0)
   * Running on http://127.0.0.1:8001
   * Running on http://192.168.178.72:8001
   Press CTRL+C to quit
   * Restarting with stat
   ```
   
4. Fill up the database with dummy data:
   ```
   python -m src.backend.prefill_database
   ```

5. Install the frontend packages:
   ```
   cd src/front-end
   npm install
   ```
6. Run the frontend application:
   ```
   npm start
   ```
   ```
   Watch mode enabled. Watching for file changes...
   NOTE: Raw file sizes do not reflect development server per-request transformations.
     ➜  Local:   http://localhost:4200/
     ➜  press h + enter to show help
   ```
