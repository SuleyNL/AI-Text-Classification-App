from src.AIService.AI_solution import AI_solution
import chromadb
from tqdm import tqdm
from PyPDF2 import PdfReader
from llama_index.core import Document
from llama_index.core.node_parser import SentenceSplitter
import ollama
from typing import List, Dict, Any
import numpy as np
from src.AIService import EmbeddingFunctions


class SentenceEmbeddingSolution(AI_solution):
    categories: List[Dict[str, Any]]
    category_embeddings: Dict

    def __init__(self, similarity_threshold=0.65):
        super().__init__()
        self.client = chromadb.Client()
        self.client.reset()
        self.collection = self.client.create_collection(
            name="docs",
            metadata={"hnsw:space": "cosine"},
            # ^^ options for hnsw:space are "l2", "cosine", and "ip".
            # See: https://docs.trychroma.com/guides#changing-the-distance-function for more info.
            embedding_function=EmbeddingFunctions.Mxbai
        )
        self.category_embeddings = self.embed_categories()
        self.similarity_threshold = similarity_threshold

    def embed_categories(self):
        category_embeddings = {}
        for category in self.categories:
            category_text = ' '.join(category['wordCloud'])
            response = ollama.embeddings(model="mxbai-embed-large", prompt=category_text)
            embedding = response["embedding"]
            category_embeddings[category['name']] = embedding
        return category_embeddings

    def get_relevant_categories(self, sentence, sentence_embedding):
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
        print("-" * 50)  # Separator for readability

        return relevant_categories

    def process_document(self, filepath: str, filename: str, person_id: str) -> str:
        # Extract text from PDF
        reader = PdfReader(filepath)
        text = ""
        for page in reader.pages:
            text += page.extract_text()

        # Create a llama_index Document object
        doc = Document(text=text)

        # TODO: below steps can be split into 2 generic functions (perhaps in the AI_solution class?)
        # 1. Split into sentences
        splitter = SentenceSplitter(chunk_size=50, chunk_overlap=5, )
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
            if relevant_categories:
                category_classes = ' '.join([category.lower().replace(' ', '_') for category in relevant_categories])
                doc_html.append(f'<span class="cat {category_classes}">{sentence}</span>')
            else:
                doc_html.append(f'<span>{sentence}</span>')


            #print(f"{sentence} stored in db with metadata filename: {filename} and person_id: {person_id}")
            #print(f"Relevant categories: {relevant_categories}")

            #doc_html.append(f"<span class=\"sociaal_netwerk financien\">{sentence}</span>")
            doc_html.append(f'<span class="{category_classes}">{sentence}</span>')

            print(f"{sentence} stored in db with metadata filename: {filename} and person_id: {person_id}")

        return ''.join(doc_html)
