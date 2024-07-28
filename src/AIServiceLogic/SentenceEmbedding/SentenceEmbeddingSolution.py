import chromadb
from PyPDF2 import PdfReader

from llama_index.core.node_parser import SentenceSplitter
from typing import List, Dict
from src.AIServiceLogic.AI_solution import AI_solution
from src.AIServiceLogic.EmbeddingFunctions.EmbeddingFunctionsModule import EmbeddingFunctions, EmbeddingFunction
from src.AIServiceLogic.SentenceEmbedding.TransformationStrategiesModule import TransformationStrategies, TransformationStrategy


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
        self.embedder: EmbeddingFunction = EmbeddingFunctions.Baai()

        self.embedding_strategy: TransformationStrategy = \
            TransformationStrategies.NoTransformation(self.embedder, self.categories)

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

        # 2. Embed and store embed the sentence-categories as classes in span elements in HTML
        doc_html = []

        # TODO: can probably be done in 1 batch, instead of for-loop
        for i, sentence in enumerate(sentences):
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
        return ''.join(doc_html)
