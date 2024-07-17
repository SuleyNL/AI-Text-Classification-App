import chromadb
from PyPDF2 import PdfReader

from llama_index.core.node_parser import SentenceSplitter
from typing import List, Dict, Sequence
import numpy as np
from src.AIServiceLogic import EmbeddingFunctions
from .AI_solution import AI_solution
from .EmbeddingFunctions import *
from .EmbeddingTransformers import TransformationStrategies, TransformationStrategy


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
        embedding_strategy (EmbeddingTransformerBase): Embedder for themes.
        client (chromadb.Client): ChromaDB client for document storage.
        collection (chromadb.Collection): ChromaDB collection for storing embeddings.
    """

    def __init__(self):
        """
        Initialize the SentenceEmbeddingSolution.

        Args:
            similarity_threshold (float, optional): Threshold for category similarity. Defaults to 0.65.

        # options for self.collection.metadata["hnsw:space"] are "l2", "cosine", and "ip".
        # See: https://docs.trychroma.com/guides#changing-the-distance-function for more info.
        """
        super().__init__()  # pre-fills categories
        self.embedder: EmbeddingFunction = EmbeddingFunctions.Mxbai()

        self.embedding_strategy = TransformationStrategies.NoTransformation(self.embedder, self.categories)

        self.client = chromadb.Client()

        self.collection = self.client.create_collection(
            name="docs",
            metadata={"hnsw:space": "cosine"},
            embedding_function=self.embedder
        )

    def get_relevant_categories_old(self, sentence: str, sentence_embedding: Sequence[float] | Sequence[int]) -> List[str]:
        """
        Get relevant categories for a given sentence based on embedding similarity.

        Args:
            sentence (str): The input sentence.
            sentence_embedding (Sequence[float] | Sequence[int]): The embedding of the input sentence.

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
        splitter = SentenceSplitter(chunk_size=50, chunk_overlap=5)
        sentences = splitter.split_text(text=text)

        # 2. Embed and store each sentence in ChromaDB collection
        doc_html = []
        for i, sentence in enumerate(sentences):
            response = self.embedder([sentence])
            # TODO: can probably be done in 1 batch, instead of individually each time
            embedding = response[0]

            self.collection.add(
                ids=[str(i)],
                embeddings=[embedding],
                documents=[sentence],
                metadatas=[{"filename": filename, "person_id": person_id}]
            )

            # Get relevant categories based on cosine similarity with the wordcloud of the category
            relevant_categories = self.embedding_strategy.get_labels(sentence)

            if relevant_categories:
                # category_classes = ' '.join([category.lower().replace(' ', '_') for category in relevant_categories])
                # Above logic is for viewing the categories directly by name, rather than their psuedonym like 'cat1'.

                category_classes_frontend = ' '.join(
                    [f'cat{self.get_category_id_by_name(category)}' for category in relevant_categories])
                doc_html.append(f'<span class="cat {category_classes_frontend}">{sentence}</span>')
            else:
                doc_html.append(f'<span>{sentence}</span>')

            print(f"{sentence} stored in db with metadata filename: {filename} and person_id: {person_id}")

        return ''.join(doc_html)
