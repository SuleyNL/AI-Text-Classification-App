from enum import Enum

from chromadb import Documents, EmbeddingFunction, Embeddings
from chromadb.api.types import Document
import ollama
from typing import List, Dict, Any, Union

from deprecation import deprecated


class Mxbai(EmbeddingFunction):
    """
    An embedding function that uses the mxbai-embed-large model from Ollama.
    """

    def __call__(self, input: Union[Document, Documents]) -> Embeddings:
        """
        Generate embeddings for the input documents.

        Args:
            input Union[Document, Documents]: A single string or a list of strings to be embedded.
            # TODO: check how this input is affected by shadow variable `input` from EmbeddingFunction class

        Returns:
            Embeddings: A list of embeddings, one for each input document.

        Example:
            mxbai = Mxbai()
            embeddings = mxbai(['this is prompt number one', 'this is another prompt'])
        """
        self.input = input
        if isinstance(self.input, Document):
            self.input = Documents([Document])

        embeddings = []
        for doc in input:
            response = ollama.embeddings(model="mxbai-embed-large", prompt=doc)
            embeddings.append(response["embedding"])
        return embeddings


class Baai(EmbeddingFunction):
    """
    An embedding function that uses the BAAI/bge-large-en-v1.5 model from huggingfaces' transformers.
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
        self.input = input
        if isinstance(self.input, Document):
            self.input = Documents([Document])

        # pipe = pipeline("feature-extraction", model="BAAI/bge-large-en-v1.5")

        # embeddings = []
        # for doc in input:
        #     embedding = pipe(doc)
        #     embeddings.append(embedding)

        from transformers import AutoTokenizer, AutoModel
        import torch

        # Load model from HuggingFace Hub
        tokenizer = AutoTokenizer.from_pretrained('BAAI/bge-large-en-v1.5')
        model = AutoModel.from_pretrained('BAAI/bge-large-en-v1.5')
        model.eval()

        # Tokenize sentences
        encoded_input = tokenizer(self.input, padding=True, truncation=True, return_tensors='pt')
        # for s2p(short query to long passage) retrieval task, add an instruction to query (not add instruction for passages)
        # encoded_input = tokenizer([instruction + q for q in queries], padding=True, truncation=True, return_tensors='pt')

        # Compute token embeddings
        with torch.no_grad():
            model_output = model(**encoded_input)
            # Perform pooling. In this case, cls pooling.
            sentence_embeddings = model_output[0][:, 0]
        # normalize embeddings
        sentence_embeddings = torch.nn.functional.normalize(sentence_embeddings, p=2, dim=1)

        # Convert tensor to list of sequences
        embeddings_list = sentence_embeddings.tolist()

        return embeddings_list


class EmbeddingFunctions(Enum):
    Baai = Baai
    Mxbai = Mxbai

    @classmethod
    def _missing_(cls, value):
        raise ValueError(f"{value} is not a valid {cls.__name__}")

    def __call__(self, *args, **kwargs) -> EmbeddingFunction:
        return self.value(*args, **kwargs)
