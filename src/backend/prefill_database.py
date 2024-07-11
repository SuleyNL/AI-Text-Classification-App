import glob
import os

import requests
import json
from datetime import datetime

# Assuming the API is running on localhost:8001
BASE_URL = "http://localhost:8001"


def create_dummy_person():
    person_data = {
        "person_name": "John Doe",
        "person_birthdate": datetime(1990, 1, 1).isoformat()
    }
    response = requests.post(f"{BASE_URL}/persons", json=person_data)
    if response.status_code == 201:
        print("Person created successfully")
        return response.json()["person_id"]
    else:
        print(f"Failed to create person: {response.text}")
        return None


def create_dummy_document(PERSON_ID, doc_path):
    metadata = {
        "doc_name": doc_path.split('\\')[-1],
        "doc_path": doc_path,
        "doc_text_path": ""
    }

    # Read the file as binary
    with open(metadata['doc_path'], 'rb') as file:
        file_content = file.read()

    response = requests.post(
        f"{BASE_URL}/persons/{PERSON_ID}/docs",
        data=file_content,
        params=metadata,
        headers={
            'Content-Type': 'application/octet-stream',
            'X-Document-Metadata': str(metadata)  # You might need to adjust this based on how your API expects metadata
        })

    if response.status_code == 201:
        print("Document created successfully")
        return response.json()["doc_id"]
    else:
        print(f"Failed to create document: {response.text}")
        return None


def create_dummy_data():
    PERSON_ID = create_dummy_person()
    print(PERSON_ID)

    # Define the directory path using raw string
    directory_path = r"..\Dummy_Data\John Doe"

    # Use glob to find all .pdf files in the directory
    pdf_files = glob.glob(os.path.join(directory_path, "*.pdf"))

    if PERSON_ID:
        for pdf in pdf_files:
            doc_id = create_dummy_document(PERSON_ID, pdf)
    print(doc_id)


if __name__ == "__main__":
    create_dummy_data()