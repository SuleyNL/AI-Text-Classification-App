import os
import glob
from pdfminer.high_level import extract_text
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai.embeddings import OpenAIEmbeddings
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.output_parsers import LangchainOutputParser

# Specify the directory containing the PDF files
directory = "C:\\Users\\suley\Downloads\\RFPs"
# Get a list of all PDF files in the directory
files = glob.glob(os.path.join(directory, '*.pdf'))

"""
import transformers
import torch
model_id = "aptha/Meta-Llama-3-8B-Instruct-Q4_0-GGUF"
pipeline = transformers.pipeline("text-generation", model=model_id, model_kwargs={"torch_dtype": torch.bfloat16}, device_map="auto")
print(pipeline("Hey how are you doing today?"))
"""

from langchain_community.llms import Ollama
llm = Ollama(model="llama3")
prompt = "Tell me a joke about llama"
result = llm.invoke(prompt)
print(result)
texts = []

# Iterate over each PDF file
for file in files:
  print(file)
  text = extract_text(file)
  texts.append(text)


from llama_index.vector_stores.qdrant import QdrantVectorStore
import qdrant_client.qdrant_client

client = qdrant_client.QdrantClient(host='localhost', port=6333)
vector_store = QdrantVectorStore(collection_name='collection_name1', client=client)

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

documents = SimpleDirectoryReader(directory).load_data()

index = VectorStoreIndex.from_documents(documents)

# Define and attach output parser
output_parser = LangchainOutputParser(lc_output_parser)
response = query_engine.query("What are some types of cost related to a RFP")
print(str(response))
