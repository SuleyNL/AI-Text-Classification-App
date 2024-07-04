from chromadb import Documents, EmbeddingFunction, Embeddings
import ollama


class Mxbai(EmbeddingFunction):
    def __call__(self, input: Documents) -> Embeddings:
        embeddings = []
        for doc in input:
            embeddings.append(ollama.embeddings(model="mxbai-embed-large", prompt=doc))
        return embeddings
