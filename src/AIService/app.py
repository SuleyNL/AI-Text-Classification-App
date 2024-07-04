# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import uuid

import requests
import json
from tqdm import tqdm
import ollama
import chromadb
from datasets import load_dataset
import umap
import matplotlib as plt
from flask import Flask, request, jsonify
from tqdm import tqdm
import llama_index.core
import os
from PyPDF2 import PdfReader
from flask import jsonify, request
import os
import uuid
from llama_index.core import Document
from llama_index.core.node_parser import SentenceSplitter
import ollama
from urllib.parse import parse_qsl


app = Flask(__name__)

client = chromadb.Client()
collection = client.create_collection(name="docs")


@app.route('/', methods=['POST'])
def hello():
    app.logger('hellokoooooorld')
    return jsonify({"hello": "korldjjj"}), 200


@app.route('/upload_doc', methods=['POST'])
def upload_doc():
    print('entered')
    if not request.data:
        print('entered2')
        return jsonify({"error": "Missing file data"}), 400

    # Parse query string
    query_string = request.query_string.decode('utf-8')
    query_params = dict(parse_qsl(query_string))

    # Extract filename from query params
    filename = query_params.get('filename')
    if not filename:
        filename = f"temp_pdf_{str(uuid.uuid4())}.pdf"
        #return jsonify({"error": "Missing filename"}), 400

    filepath = os.path.join(os.getcwd(), "uploads", filename)

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'wb') as f:
        f.write(request.data)

    try:
        # Extract text from PDF
        reader = PdfReader(filepath)
        text = ""
        for page in reader.pages:
            text += page.extract_text()

        # Create a Document object
        doc = Document(text=text)

        # Split into sentences
        splitter = SentenceSplitter(chunk_size=50, chunk_overlap=5, )
        nodes = splitter.get_nodes_from_documents([doc])
        sentences = [node.text for node in nodes]

        # Process sentences using add_doc logic
        chunks = 0
        for i, sentence in enumerate(sentences):
            response = ollama.embeddings(model="mxbai-embed-large", prompt=sentence)
            embedding = response["embedding"]
            collection.add(
                ids=[str(i)],
                embeddings=[embedding],
                documents=[sentence],
                metadatas=[{"filename": filename}]
            )
            print(sentence)
            chunks += 1

    finally:
        # Cleanup temporary file
        os.remove(filepath)

    return jsonify({"message": f"{chunks} chunks added successfully"})


def add_sentences():
    prompts = request.json.get('prompts', [])
    if not isinstance(prompts, list):
        return jsonify({"error": "Invalid input, expected a list of prompts"}), 400

    for i, d in tqdm(enumerate(prompts)):
        response = ollama.embeddings(model="mxbai-embed-large", prompt=d)
        embedding = response["embedding"]
        collection.add(
            ids=[str(i)],
            embeddings=[embedding],
            documents=[d]
        )

    return jsonify({"message": "Sentences added successfully"})


@app.route('/ask', methods=['POST'])
def ask_db():
    question = request.json.get('question', [])
    # an example prompt
    # generate an embedding for the prompt and retrieve the most relevant doc
    response = ollama.embeddings(
        prompt=question,
        model="mxbai-embed-large"
    )
    results = collection.query(
        query_embeddings=[response["embedding"]],
        n_results=10
    )
    data = results
    return data


def to_umap():
    standard_embedding = umap.UMAP(random_state=42).fit_transform(mnist.data)
    plt.scatter(standard_embedding[:, 0], standard_embedding[:, 1], c=mnist.target.astype(int), s=0.1, cmap='Spectral');


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, use_reloader=True, debug=True)
