from chromadb import Documents, EmbeddingFunction, Embeddings
import numpy as np
import ollama
from typing import List, Dict, Any


class Mxbai(EmbeddingFunction):
    """
    An embedding function that uses the mxbai-embed-large model from Ollama.

    This class implements the EmbeddingFunction interface from chromadb
    to provide embeddings for documents using the mxbai-embed-large model.
    """

    def __call__(self, input: Documents) -> Embeddings:
        """
        Generate embeddings for the input documents.

        Args:
            input (Documents): A list of document strings to be embedded.

        Returns:
            Embeddings: A list of embeddings, one for each input document.
        """
        embeddings = []
        for doc in input:
            response = ollama.embeddings(model="mxbai-embed-large", prompt=doc)
            embeddings.append(response["embedding"])
        return embeddings


class ThemeEmbedder:
    """
    A class for embedding themes and comparing sentence embeddings to theme embeddings.

    This class creates embeddings for themes, applies transformation matrices to
    emphasize theme-specific dimensions, and computes similarities between
    sentences and themes.

    Attributes:
        themes (List[Dict[str, List[str]]]): A list of theme dictionaries.
        theme_embeddings (Dict[str, np.ndarray]): Embeddings for each theme.
        transformation_matrices (Dict[str, np.ndarray]): Transformation matrices for each theme.
        negative_embedding (np.ndarray): An embedding representing common, non-theme-specific words.
    """

    def __init__(self, themes: List[Dict[str, List[str]]], alpha: float = 0.51):
        """
        Initialize the ThemeEmbedder.

        Args:
            themes (List[Dict[str, List[str]]]): A list of theme dictionaries.
            alpha (float, optional): Weight factor for theme projection matrix. Defaults to 0.51.
        """
        self.themes = themes
        self.theme_embeddings = self._create_theme_embeddings()
        self.transformation_matrices = self._create_transformation_matrices(alpha)
        self.negative_embedding = self._create_negative_embedding()

    def _create_theme_embeddings(self) -> Dict[str, np.ndarray]:
        """
        Create embeddings for each theme based on its word cloud.

        Returns:
            Dict[str, np.ndarray]: A dictionary mapping theme names to their embeddings.
        """
        theme_embeddings = {}
        for theme in self.themes:
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
        response = ollama.embeddings(model="mxbai-embed-large", prompt=text)
        return np.array(response["embedding"])

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

    def get_theme_similarities(self, sentence_embedding: np.ndarray) -> Dict[str, float]:
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