from src.AIServiceLogic.AI_solution import AI_solution
import chromadb
from tqdm import tqdm
from PyPDF2 import PdfReader
from llama_index.core import Document
from llama_index.core.node_parser import SentenceSplitter
import ollama
from typing import List, Dict, Any
import numpy as np
from src.AIServiceLogic import EmbeddingFunctions


class SentenceEmbeddingSolution(AI_solution):
    """
    A solution for embedding sentences and categorizing document content.

    This class extends AI_solution to provide functionality for embedding sentences,
    categorizing them based on similarity to predefined categories, and processing
    documents to generate labeled HTML output.

    Attributes:
        categories (List[Dict[str, Any]]): List of category dictionaries, each containing
                                           'id', 'name', and 'wordCloud' keys.
        category_embeddings (Dict[str, List[float]]): Embeddings for each category's word cloud.
        theme_embedder (EmbeddingFunctions.ThemeEmbedder): Embedder for themes.
        client (chromadb.Client): ChromaDB client for document storage.
        collection (chromadb.Collection): ChromaDB collection for storing embeddings.
        similarity_threshold (float): Threshold for determining category relevance.
    """

    def __init__(self, similarity_threshold: float = 0.65):
        """
        Initialize the SentenceEmbeddingSolution.

        Args:
            similarity_threshold (float, optional): Threshold for category similarity. Defaults to 0.65.
        """
        super().__init__() # pre-fills categories
        self.theme_embedder = EmbeddingFunctions.ThemeEmbedder(self.categories)
        self.client = chromadb.Client()
        self.collection = self.client.create_collection(
            name="docs",
            metadata={"hnsw:space": "cosine"}
        )
        # ^^ options for "hnsw:space" are "l2", "cosine", and "ip".
        # See: https://docs.trychroma.com/guides#changing-the-distance-function for more info.
        # embedding_function=EmbeddingFunctions.Mxbai

        self.category_embeddings = self.embed_categories()
        self.similarity_threshold = similarity_threshold

    def embed_categories(self) -> Dict[str, List[float]]:
        """
        Embed all categories using their word clouds.

        Returns:
            Dict[str, List[float]]: A dictionary mapping category names to their embeddings.
        """
        category_embeddings = {}
        for category in self.categories:
            category_text = ' '.join(category['wordCloud'])
            response = ollama.embeddings(model="mxbai-embed-large", prompt=category_text)
            embedding = response["embedding"]
            category_embeddings[category['name']] = embedding
        return category_embeddings

    def get_relevant_themes(self, sentence: str) -> List[str]:
        """
        Get relevant themes for a given sentence based on embedding similarity.

        Args:
            sentence (str): The input sentence.

        Returns:
            List[str]: A list of relevant theme names.
        """
        sentence_embedding = self.theme_embedder.get_sentence_embedding(sentence)
        similarities = self.theme_embedder.get_theme_similarities(sentence_embedding)

        relevant_themes = []
        print(f"Sentence: {sentence}")
        print("Theme similarities:")
        for theme, similarity in similarities.items():
            print(f"  {theme}: {similarity:.4f}")
            if similarity >= self.similarity_threshold:
                relevant_themes.append(theme)

        print(f"Relevant themes: {relevant_themes}")
        print("-" * 50)

        return relevant_themes

    def get_relevant_categories(self, sentence: str, sentence_embedding: List[float]) -> List[str]:
        """
        Get relevant categories for a given sentence based on embedding similarity.

        Args:
            sentence (str): The input sentence.
            sentence_embedding (List[float]): The embedding of the input sentence.

        Returns:
            List[str]: A list of relevant category names.
        """
        relevant_categories = []
        print(f"Sentence: {sentence}")
        print("Category similarities:")

        for category_name, category_embedding in self.category_embeddings.items():
            similarity = np.dot(sentence_embedding, category_embedding) / (
                    np.linalg.norm(sentence_embedding) * np.linalg.norm(category_embedding)
            )
            print(f"  {category_name}: {similarity:.4f}")

            if similarity >= self.similarity_threshold:
                relevant_categories.append(category_name)

        print(f"Relevant categories: {relevant_categories}")
        print("-" * 50)

        return relevant_categories

    def process_document(self, filepath: str, filename: str, person_id: int) -> str:
        """
        Process a document, extract text, split into sentences, embed, and categorize.

        Args:
            filepath (str): The path to the document file.
            filename (str): The name of the document file.
            person_id (int): The ID of the person associated with the document.

        Returns:
            str: HTML string with categorized sentences.
        """
        # Extract text from PDF
        reader = PdfReader(filepath)
        text = "".join(page.extract_text() for page in reader.pages)

        # TODO: below steps can be split into 2 generic functions (perhaps in the AI_solution class?)
        # 1. Split into sentences
        doc = Document(text=text)
        splitter = SentenceSplitter(chunk_size=50, chunk_overlap=5)
        nodes = splitter.get_nodes_from_documents([doc])
        sentences = [node.text for node in nodes]

        # 2. Embed and store each sentence in ChromaDB collection
        doc_html = []
        for i, sentence in enumerate(sentences):
            response = ollama.embeddings(model="mxbai-embed-large", prompt=sentence)
            embedding = response["embedding"]

            self.collection.add(
                ids=[str(i)],
                embeddings=[embedding],
                documents=[sentence],
                metadatas=[{"filename": filename, "person_id": person_id}]
            )

            # Get relevant categories based on cosine similarity with the wordcloud of the category
            relevant_categories = self.get_relevant_categories(sentence, embedding)
            #relevant_categories = self.get_relevant_themes(sentence)

            if relevant_categories:
                category_classes = ' '.join([category.lower().replace(' ', '_') for category in relevant_categories])
                category_classes_frontend = ' '.join(
                    [f'cat{self.get_category_id_by_name(category)}' for category in relevant_categories])
                doc_html.append(f'<span class="cat {category_classes_frontend}">{sentence}</span>')
            else:
                doc_html.append(f'<span>{sentence}</span>')

            print(f"{sentence} stored in db with metadata filename: {filename} and person_id: {person_id}")

        return ''.join(doc_html)
