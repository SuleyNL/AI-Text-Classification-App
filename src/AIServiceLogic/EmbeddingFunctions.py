from chromadb import Documents, EmbeddingFunction, Embeddings
from chromadb.api.types import Document
import ollama
from typing import List, Dict, Any, Union

from deprecation import deprecated
from transformers import pipeline


class Mxbai(EmbeddingFunction):
    """
    An embedding function that uses the mxbai-embed-large model from Ollama.
    """

    def __call__(self, input: Documents) -> Embeddings:
        """
        Generate embeddings for the input documents.

        Args:
            input Union[Document, Documents]: A single string or a list of strings to be embedded.
            # TODO: check how this input is affected by shadow variable `input` from EmbeddingFunction class

        Returns:
            Embeddings: A list of embeddings, one for each input document.

        Example:
            mxbai = Mxbai()
            embeddings = mxbai(['this is prompt number one', 'this is the second prompt'])
        """
        embeddings = []
        if type(input) == Document:
            input = [Document]
        for doc in input:
            response = ollama.embeddings(model="mxbai-embed-large", prompt=doc)
            embeddings.append(response["embedding"])
        return embeddings


@deprecated(details="This function is not ready for production use. " 
                    "Expected each value in the embedding to be an int or float, got a nested list instead.")
class Baai(EmbeddingFunction):
    """
    An embedding function that uses the BAAI/bge-large-en-v1.5 model from huggingfaces' transformers.
    # TODO: this function is Expected to return each value in the embedding as an int or float,
        # got an embedding with ['list'] - [[[-0.10573101043701172, 0.3996315598487854, ...]]]
        # Yet has to be fixed
    """

    def __call__(self, input: Documents) -> Embeddings:
        """
        Generate embeddings for the input documents.

        Args:
            input (Documents): A single string or a list of strings to be embedded.

        Returns:
            Embeddings: A list of embeddings, one for each input document.

        Example:
            baai = Baai()
            embeddings = baai(['this is prompt number one', 'this is the second prompt'])
        """
        pipe = pipeline("feature-extraction", model="BAAI/bge-large-en-v1.5")
        return pipe(input)
