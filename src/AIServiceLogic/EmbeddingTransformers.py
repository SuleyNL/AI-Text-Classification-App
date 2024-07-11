from typing import Dict, List, Sequence, Union
from chromadb import EmbeddingFunction, Embeddings

import numpy as np
from src.AIServiceLogic import EmbeddingFunctions, EmbeddingTransformerBase
from src.AIServiceLogic.EmbeddingTransformerBase import EmbeddingTransformerBase


class EmptyTransformer2(EmbeddingTransformerBase):
    """
    A class that mimics ThemeTransformer but doesn't modify any embeddings.

    This class has the same method signatures as ThemeTransformer and calculates
    similarities without modifying embeddings.

    Attributes:
        categories (List[Dict[str, List[str]]]): A list of theme dictionaries.
        embedder (callable): A function to generate embeddings.
        theme_embeddings (Dict[str, np.ndarray]): Embeddings for each theme.
    """

    def __init__(self, categories: List[Dict[str, List[str]]], alpha: float = 0.51, embedder: callable = None):
        """
        Initialize the EmptyTransformer.

        Args:
            categories (List[Dict[str, List[str]]]): A list of theme dictionaries.
            alpha (float, optional): Unused. Kept for compatibility.
            embedder (callable, optional): A function to generate embeddings.
        """
        super().__init__(embedder)
        self.categories = categories
        self.embedder = embedder
        self.theme_embeddings = self._create_theme_embeddings()

    def get_sentence_embedding(self, sentence: str) -> np.ndarray:
        """
        Get the embedding for a given sentence without modification.

        Args:
            sentence (str): The input sentence to embed.

        Returns:
            np.ndarray: The unmodified embedding of the input sentence.
        """
        embedding = self.embedder([sentence])[0]

        # Prove that the embedding is not changed
        original_embedding = np.array(embedding)
        assert np.array_equal(embedding, original_embedding), "Embedding should not be modified"

        return embedding

    def get_category_similarities(self, sentence_embedding: np.ndarray) -> Dict[str, float]:
        """
        Calculate similarities between a sentence embedding and all theme embeddings.

        Args:
            sentence_embedding (np.ndarray): The embedding of the input sentence.

        Returns:
            Dict[str, float]: A dictionary mapping theme names to their similarity scores.
        """
        # Prove that the sentence_embedding is not changed
        original_embedding = np.array(sentence_embedding)
        assert np.array_equal(sentence_embedding, original_embedding), "Sentence embedding should not be modified"

        similarities = {}
        for theme_name, theme_embedding in self.theme_embeddings.items():
            similarity = self._cosine_similarity(sentence_embedding, theme_embedding)
            similarities[theme_name] = similarity
        return similarities

    def _create_theme_embeddings(self) -> Dict[str, np.ndarray]:
        """
        Create embeddings for each theme based on its word cloud.

        Returns:
            Dict[str, np.ndarray]: A dictionary mapping theme names to their embeddings.
        """
        theme_embeddings = {}
        for theme in self.categories:
            theme_name = theme['name']
            word_cloud = theme['wordCloud']
            embeddings = self.embedder(word_cloud)
            theme_embeddings[theme_name] = np.mean(embeddings, axis=0)
        return theme_embeddings

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """
        Calculate the cosine similarity between two vectors.

        Args:
            a (np.ndarray): First vector.
            b (np.ndarray): Second vector.

        Returns:
            float: Cosine similarity between the two vectors.
        """
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def _get_embedding(self, text: str) -> np.ndarray:
        """
        Get the embedding for a given text without modification.

        Args:
            text (str): The input text to embed.

        Returns:
            np.ndarray: The unmodified embedding of the input text.
        """
        embedding = self.embedder([text])[0]

        # Prove that the embedding is not changed
        original_embedding = np.array(embedding)
        assert np.array_equal(embedding, original_embedding), "Embedding should not be modified"

        return embedding


class EmptyTransformer(EmbeddingTransformerBase):
    def _get_embedding(self, sentence: str) -> Embeddings:
        return self.embedder([sentence])

    def get_sentence_embedding(self, sentence: str) -> List[Sequence[float] | Sequence[int]]:
        pass

    def __init__(self,
                 categories: List[Dict[str, List[str]]],
                 embedder: EmbeddingFunction = EmbeddingFunctions.Mxbai):
        super().__init__(embedder)  # Call the parent class constructor with the embedder
        self.embedder = embedder
        self.categories = categories
        self.theme_embeddings = self._create_category_embeddings()

    def _create_category_embeddings(self) -> Dict[str, np.ndarray]:
        """
        Create embeddings for each category based on its word cloud.

        Returns:
            Dict[str, np.ndarray]: A dictionary mapping category names to their embeddings.
        """
        theme_embeddings = {}
        for theme in self.categories:
            theme: dict
            theme_name: str = theme['name']
            word_cloud: List[str] = theme['wordCloud']
            # Old= embeddings: List[np.ndarray] = [self._get_embedding(word) for word in word_cloud]
            embeddings: List[Union[List[Sequence[float]], Sequence[int]]] = [self._get_embedding(word)[0] for word in word_cloud]
            # Convert the list of embeddings to a numpy array
            embeddings_array: np.ndarray = np.array(embeddings)
            theme_embeddings[theme_name]: np.ndarray = np.mean(embeddings_array, axis=0)
        return theme_embeddings

    def get_category_similarities(self, sentence_embedding: np.ndarray) -> Dict[str, float]:
        similarities = {}
        for theme_name, theme_embedding in self.theme_embeddings.items():
            similarity = self._cosine_similarity(sentence_embedding, theme_embedding)
            similarities[theme_name] = similarity
        return similarities


class ThemeTransformer(EmbeddingTransformerBase):
    """
    A class for embedding themes and comparing sentence embeddings to theme embeddings.

    This class creates embeddings for themes, applies transformation matrices to
    emphasize theme-specific dimensions, and computes similarities between
    sentences and themes.

    Attributes:
        categories (List[Dict[str, List[str]]]): A list of theme dictionaries.
        theme_embeddings (Dict[str, np.ndarray]): Embeddings for each theme.
        transformation_matrices (Dict[str, np.ndarray]): Transformation matrices for each theme.
        negative_embedding (np.ndarray): An embedding representing common, non-theme-specific words.
        embedder (EmbeddingFunction): An embedding function which transforms text into its vector-representation
    """

    def __init__(self,
                 categories: List[Dict[str, List[str]]],
                 alpha: float = 0.51,
                 embedder: EmbeddingFunction = EmbeddingFunctions.Mxbai):
        """
        Args:
            categories (List[Dict[str, List[str]]]): A list of theme dictionaries.
            alpha (float, optional): Weight factor for theme projection matrix. Defaults to 0.51.
        """
        super().__init__(embedder)  # Call the parent class constructor with the embedder
        self.categories = categories
        self.theme_embeddings = self._create_theme_embeddings()
        self.transformation_matrices = self._create_transformation_matrices(alpha)
        self.negative_embedding = self._create_negative_embedding()
        self.embedder = embedder

    def get_sentence_embedding(self, sentence: str) -> np.ndarray:
        """
        Get the embedding for a given sentence.

        This method currently returns the raw embedding without subtracting
        the negative embedding. The subtraction is commented out for potential
        future experimentation.

        Args:
            sentence (str): The input sentence to embed.

        Returns:
            np.ndarray: The embedding of the input sentence.
        """
        return self._get_embedding(sentence)  # - self.negative_embedding #TODO: For later experimentation

    def get_category_similarities(self, sentence_embedding: np.ndarray) -> Dict[str, float]:
        """
        Calculate similarities between a sentence embedding and all theme embeddings.

        This method applies the theme-specific transformation matrices to the
        sentence embedding before calculating cosine similarity with each theme.

        Args:
            sentence_embedding (np.ndarray): The embedding of the input sentence.

        Returns:
            Dict[str, float]: A dictionary mapping theme names to their similarity scores.
        """
        similarities = {}
        for theme_name, theme_embedding in self.theme_embeddings.items():
            transformed_sentence_embedding = np.dot(sentence_embedding, self.transformation_matrices[theme_name])
            similarity = self._cosine_similarity(transformed_sentence_embedding, theme_embedding)
            similarities[theme_name] = similarity
        return similarities

    def _create_theme_embeddings(self) -> Dict[str, np.ndarray]:
        """
        Create embeddings for each theme based on its word cloud.

        Returns:
            Dict[str, np.ndarray]: A dictionary mapping theme names to their embeddings.
        """
        theme_embeddings = {}
        for theme in self.categories:
            theme: dict
            theme_name: str = theme['name']
            word_cloud: List[str] = theme['wordCloud']
            embeddings: List[np.ndarray] = [self._get_embedding(word) for word in word_cloud]
            theme_embeddings[theme_name]: np.ndarray = np.mean(embeddings, axis=0)
        return theme_embeddings

    def _create_transformation_matrices(self, alpha: float) -> Dict[str, np.ndarray]:
        """
        Create transformation matrices for each theme.

        Args:
            alpha (float): Weight factor for theme projection matrix.

        Returns:
            Dict[str, np.ndarray]: A dictionary mapping theme names to their transformation matrices.
        """
        transformation_matrices = {}
        for theme_name, theme_embedding in self.theme_embeddings.items():
            identity = np.eye(len(theme_embedding))
            theme_matrix = np.outer(theme_embedding, theme_embedding)
            matrix = (1 - alpha) * identity + alpha * theme_matrix
            transformation_matrices[theme_name] = matrix
        return transformation_matrices

    def _create_negative_embedding(self) -> np.ndarray:
        """
        Create an embedding representing common, non-theme-specific words.

        Returns:
            np.ndarray: The negative embedding.
        """
        negative_words = ["de", "het", "tafel", "bord", "automaat", "laptop", "plastic", "whiteboard", "naar", "over",
                          "rapport", "verklaring"]
        negative_embeddings = [self._get_embedding(word) for word in negative_words]
        return np.mean(negative_embeddings, axis=0)

    def _get_embedding(self, text: str) -> np.ndarray:
        """
        Get the embedding for a given text using the mxbai-embed-large model.

        Args:
            text (str): The input text to embed.

        Returns:
            np.ndarray: The embedding of the input text.
        """
        # response = ollama.embeddings(model="mxbai-embed-large", prompt=text)
        # return np.array(response["embedding"])

        response = self.embedder([text])[0]
        return np.array(response)

