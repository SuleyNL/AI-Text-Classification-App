import time
import requests
import json
import ollama
import chromadb

documents = [
  "Llamas are members of the camelid family meaning they're pretty closely related to vicuñas and camels",
  "Llamas were first domesticated and used as pack animals 4,000 to 5,000 years ago in the Peruvian highlands",
  "Llamas can grow as much as 6 feet tall though the average llama between 5 feet 6 inches and 5 feet 9 inches tall",
  "Llamas weigh between 280 and 450 pounds and can carry 25 to 30 percent of their body weight",
  "Llamas are vegetarians and have very efficient digestive systems",
  "Llamas live to be about 20 years old, though some only live for 15 years and others live to be 30 years old",
]

client = chromadb.Client()
collection = client.create_collection(name="docs")

# store each document in a vector embedding database
for i, d in enumerate(documents):
  response = ollama.embeddings(model="mxbai-embed-large", prompt=d)
  embedding = response["embedding"]
  collection.add(
    ids=[str(i)],
    embeddings=[embedding],
    documents=[d]
  )


# an example prompt
prompt = "What animals are llamas related to?"

# generate an embedding for the prompt and retrieve the most relevant doc
response = ollama.embeddings(
  prompt=prompt,
  model="mxbai-embed-large"
)
results = collection.query(
  query_embeddings=[response["embedding"]],
  n_results=1
)
data = results['documents'][0][0]



i = 0
while i < 5:
    print("hello world")

    # URL van de andere container's endpoint
    url = "http://ollama:11434/api/chat"
    #url = "http://localhost:11434/api/chat" without docker


    # Het bericht dat we willen versturen
    data = {
        "model": "llama3",
        "messages": [
            {"role": "user", "content": "why is the sky blue?"}
        ]
    }

    try:
        # Send the initial request
        response = requests.post(url, json=data, stream=True)

        # Process each JSON response
        for line in response.iter_lines():
            if line:
                # Parse the JSON response
                json_data = line.decode('utf-8')
                parsed_data = json.loads(json_data)

                # Extract and print the content
                content = parsed_data['message']['content']
                print(content)

    except Exception as e:
        print("An error occurred:", e)

    i += 1
    time.sleep(3)
