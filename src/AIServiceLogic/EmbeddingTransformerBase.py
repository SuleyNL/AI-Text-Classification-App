import abc
from typing import Dict, Sequence, List

import numpy as np
from chromadb import EmbeddingFunction, Embeddings
from src.AIServiceLogic import EmbeddingFunctions


class EmbeddingTransformerBase(abc.ABC):
    def __init__(self, embedder: EmbeddingFunction = EmbeddingFunctions.Mxbai):
        self.embedder = embedder

    @abc.abstractmethod
    def get_sentence_embedding(self, sentence: str) -> Sequence[float] | Sequence[int]:
        """
        Abstract method to get the embedding for a sentence.

        Args:
            sentence (str): The input sentence to embed.

        Returns:
            np.ndarray: The embedding of the input sentence.
        """
        return self._get_embedding(sentence)[0]

    @abc.abstractmethod
    def get_category_similarities(self, sentence_embedding: np.ndarray) -> Dict[str, float]:
        """
        Calculate similarities between a sentence embedding and all category embeddings.

        This method applies the theme-specific transformation matrices to the
        sentence embedding before calculating cosine similarity with each theme.

        Args:
            sentence_embedding (np.ndarray): The embedding of the input sentence.

        Returns:
            Dict[str, float]: A dictionary mapping theme names to their similarity scores.
        """
        pass

    @abc.abstractmethod
    def _get_embedding(self, sentence: str) -> Embeddings:
        """
        Internal method to get the raw embedding for a given sentence.

        Args:
            sentence (str): The input sentence to embed.

        Returns:
            np.ndarray: The raw embedding of the input sentence.
        """
        return self.embedder([sentence])

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate the cosine similarity between two vectors.

        Args:
            vec1 (np.ndarray): The first vector.
            vec2 (np.ndarray): The second vector.

        Returns:
            float: The cosine similarity between the two vectors.
        """
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
