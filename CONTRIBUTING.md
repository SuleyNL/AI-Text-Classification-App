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
If you are ready to contribute but dont know where to get started please see the 
[README about Setup and Installation](README.md#setup-and-installation)
