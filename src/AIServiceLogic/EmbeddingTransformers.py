from typing import Dict, List, Sequence, Union, Any
from chromadb import EmbeddingFunction, Embeddings

import numpy as np
from src.AIServiceLogic import EmbeddingFunctions
from src.AIServiceLogic.EmbeddingTransformerBase import EmbeddingTransformerBase


class EmptyTransformer(EmbeddingTransformerBase):
    """
    A class of the type EmbeddingTransformerBase that doesn't modify any embeddings.

    This class has the same method signatures as a regular EmbeddingTransformerBase but calculates
    similarities without modifying embeddings.

    Attributes:
        categories (List[Dict[str, List[str]]]): A list of theme dictionaries.
        embedder (callable): A function to generate embeddings.
        theme_embeddings (Dict[str, np.ndarray]): Embeddings for each theme.
    """
    def get_sentence_embedding(self, sentence: str) -> np.ndarray:
        return np.array(self._get_embedding(sentence)[0])

    def _get_embedding(self, text: str) -> Embeddings:
        return self.embedder([text])

    def __init__(self, categories: List[Dict[str, List[str]]], embedder: EmbeddingFunction = EmbeddingFunctions.Mxbai):
        """
        Initialize the EmptyTransformer.

        Args:
            categories (List[Dict[str, List[str]]]): A list of theme dictionaries.
            embedder (EmbeddingFunction, optional): A function to generate embeddings.
        """
        super().__init__(embedder)
        self.categories = categories
        self.embedder = embedder
        self.theme_embeddings = self._create_theme_embeddings()

    def get_category_similarities(self, sentence_embedding: np.ndarray) -> Dict[str, float]:
        """
        Calculate similarities between a sentence embedding and all theme embeddings.

        Args:
            sentence_embedding (np.ndarray): The embedding of the input sentence.

        Returns:
            Dict[str, float]: A dictionary mapping theme names to their similarity scores.
        """
        similarities = {}
        for theme_name, theme_embedding in self.theme_embeddings.items():
            similarity = self._cosine_similarity(sentence_embedding, theme_embedding)
            similarities[theme_name] = similarity
        return similarities

    def _create_theme_embeddings(self) -> dict[str, np.ndarray]:
        """
        Create embeddings for each theme based on its word cloud.

        Returns:
            dict[str, np.ndarray]: A dictionary mapping theme names to their embeddings.
        """
        theme_embeddings = {}
        for theme in self.categories:
            theme_name = theme['name']
            word_cloud = theme['wordCloud']
            embeddings = self.embedder(word_cloud)
            theme_embeddings[theme_name] = np.mean(embeddings, axis=0)
        print('theme embeddings = ')
        print(theme_embeddings)
        return theme_embeddings


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
        return self._get_embedding(sentence)[0]  # - self.negative_embedding #TODO: For later experimentation

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
            embeddings: List[np.ndarray] = [self._get_embedding(word)[0] for word in word_cloud]
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
        negative_embeddings = [self._get_embedding(word)[0] for word in negative_words]
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

