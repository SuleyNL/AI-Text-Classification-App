from typing import Dict, List, Any
import numpy as np
from abc import ABC, abstractmethod
from enum import Enum
from chromadb import EmbeddingFunction
from chromadb.api.types import Embedding
from deprecation import deprecated


class TransformationStrategy(ABC):
    category_embeddings: Dict[str, np.array]
    embedder: EmbeddingFunction
    similarity_threshold: float

    def __init__(self, embedder: EmbeddingFunction, categories: List[Dict[str, Any]]):
        self.embedder = embedder
        self.category_embeddings = self._create_category_embeddings(categories)
        pass

    @abstractmethod
    def get_labels(self, sentence: str) -> List[str]:
        """
        [Mandatory inheritance function]

        Returns relevant categories for a given sentence based on embedding similarity
        and (optionally) matrix transformations performed by the embedder.

        Args:
            sentence (str): The input sentence.

        Returns:
            List[str]: A list of relevant theme names.
        """
        pass

    def _get_embedding(self, text: str) -> Embedding:
        return self.embedder([text])[0]

    def _create_category_embeddings(self, categories: List[Dict[str, Any]]) -> dict[str, np.array]:
        """
        Embed all categories using their word clouds.

        Returns:
            Dict[str, List[float]]: A dictionary mapping category names to their embeddings.
        """
        category_embeddings = {}
        for category in categories:
            category_text = ' '.join(category['wordCloud'])
            embedding = self._get_embedding(category_text)
            category_embeddings[category['name']] = np.array(embedding)
        return category_embeddings


class NoTransformation(TransformationStrategy):
    similarity_threshold = 0.65

    def __init__(self, embedder: EmbeddingFunction, categories):
        super().__init__(embedder, categories)
        self.category_embeddings = self._create_category_embeddings(categories)

    def get_labels(self, sentence: str) -> List[str]:
        sentence_embedding = np.array(self._get_embedding(sentence))
        similarities = self._calculate_sentence_similarity_to_categories(sentence_embedding)

        relevant_categories = []
        print(f"Sentence: {sentence}")
        print("Theme similarities:")
        for theme, similarity in similarities.items():
            print(f"  {theme}: {similarity:.4f}")
            if similarity >= self.similarity_threshold:
                relevant_categories.append(theme)

        print(f"Relevant themes: {relevant_categories}")
        print("-" * 50)

        return relevant_categories

    def _calculate_sentence_similarity_to_categories(self, sentence_embedding: np.array) -> Dict[str, float]:
        return {theme_name: self._calculate_similarity(sentence_embedding, theme_embedding)
                for theme_name, theme_embedding in self.category_embeddings.items()}

    def _calculate_similarity(self, sentence_embedding: np.array, theme_embedding: np.array) -> float:
        return np.dot(sentence_embedding, theme_embedding) / (
                np.linalg.norm(sentence_embedding) * np.linalg.norm(theme_embedding))


@deprecated(details="This TransformationStrategy is not ready for production use yet")
class ThemeTransformation(TransformationStrategy):
    def get_labels(self, sentence: str) -> List[str]:
        pass

    def __init__(self, embedder: EmbeddingFunction, categories: List[Dict[str, Any]]):
        super().__init__(embedder, categories)
        self.alpha = 0.51
        self.transformation_matrices = self._create_transformation_matrices()
        self.negative_embedding = self._create_negative_embedding()

    def transform_embedding(self, embedding: np.array) -> np.array:
        return embedding - self.negative_embedding

    def transform_similarity(self, sentence_embedding: np.array, theme_embedding: np.array) -> float:
        theme_name = next(
            name for name, emb in self.transformation_matrices.items() if np.array_equal(emb, theme_embedding))
        transformed_sentence_embedding = np.dot(sentence_embedding, self.transformation_matrices[theme_name])
        return np.dot(transformed_sentence_embedding, theme_embedding) / (
                np.linalg.norm(transformed_sentence_embedding) * np.linalg.norm(theme_embedding))

    def _create_negative_embedding(self) -> np.array:
        negative_words = ["de", "het", "tafel", "bord", "automaat", "laptop", "plastic", "whiteboard", "naar", "over",
                          "rapport", "verklaring"]
        return np.mean([self._get_embedding(word)[0] for word in negative_words], axis=0)

    def _create_transformation_matrices(self) -> Dict[str, np.array]:
        return {
            theme_name: (1 - self.alpha) * np.eye(len(theme_embedding)) + self.alpha * np.outer(theme_embedding, theme_embedding)
            for theme_name, theme_embedding in self.category_embeddings.items()}

    def _create_category_embeddings(self, categories) -> Dict[str, np.array]:
        return {theme['name']: np.mean([self._get_embedding(word)[0] for word in theme['wordCloud']], axis=0)
                for theme in self.categories}


class TransformationStrategies(Enum):
    ThemeTransformation = ThemeTransformation
    NoTransformation = NoTransformation

    @classmethod
    def _missing_(cls, value):
        raise ValueError(f"{value} is not a valid {cls.__name__}")

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        for name, value in cls.__members__.items():
            if not issubclass(value.value, TransformationStrategy):
                raise TypeError(f"{name} must be a subclass of TransformationStrategy")

    def __call__(self, *args, **kwargs) -> TransformationStrategy:
        return self.value(*args, **kwargs)


