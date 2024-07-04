from chromadb import Documents, EmbeddingFunction, Embeddings
import ollama
import numpy as np
import ollama
from typing import List, Dict, Any


class Mxbai(EmbeddingFunction):
    def __call__(self, input: Documents) -> Embeddings:
        embeddings = []
        for doc in input:
            embeddings.append(ollama.embeddings(model="mxbai-embed-large", prompt=doc))
        return embeddings


class ThemeEmbedder:
    def __init__(self, themes: List[Dict[str, List[str]]], alpha: float = 0.5):
        self.themes = themes
        self.theme_embeddings = self._create_theme_embeddings()
        self.transformation_matrices = self._create_transformation_matrices(alpha)
        self.negative_embedding = self._create_negative_embedding()

    def _create_theme_embeddings(self):
        theme_embeddings = {}
        for theme in self.themes:
            theme_name = theme['name']
            word_cloud = theme['wordCloud']
            embeddings = [self._get_embedding(word) for word in word_cloud]
            theme_embeddings[theme_name] = np.mean(embeddings, axis=0)
        return theme_embeddings

    def _create_transformation_matrices(self, alpha: float):
        transformation_matrices = {}
        for theme_name, theme_embedding in self.theme_embeddings.items():
            # Create a matrix that is a weighted sum of the identity matrix and the theme projection matrix
            identity = np.eye(len(theme_embedding))
            theme_matrix = np.outer(theme_embedding, theme_embedding)
            matrix = (1 - alpha) * identity + alpha * theme_matrix
            transformation_matrices[theme_name] = matrix
        return transformation_matrices

    def _create_transformation_matrices_old(self):
        transformation_matrices = {}
        for theme_name, theme_embedding in self.theme_embeddings.items():
            matrix = np.outer(theme_embedding, theme_embedding)
            transformation_matrices[theme_name] = matrix
        return transformation_matrices

    def _create_negative_embedding(self):
        negative_words = ["the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for"]
        negative_embeddings = [self._get_embedding(word) for word in negative_words]
        return np.mean(negative_embeddings, axis=0)

    def _get_embedding(self, text: str):
        response = ollama.embeddings(model="mxbai-embed-large", prompt=text)
        return np.array(response["embedding"])

    def get_sentence_embedding(self, sentence: str):
        return self._get_embedding(sentence)  # - self.negative_embedding #TODO: For later experimentation

    def get_theme_similarities(self, sentence_embedding: np.ndarray):
        similarities = {}
        for theme_name, theme_embedding in self.theme_embeddings.items():
            transformed_sentence_embedding = np.dot(sentence_embedding, self.transformation_matrices[theme_name])
            similarity = self._cosine_similarity(transformed_sentence_embedding, theme_embedding)
            similarities[theme_name] = similarity
        return similarities

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray):
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
