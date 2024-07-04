import abc
import json
import os
from typing import List, Dict, Any


class AI_solution(abc.ABC):

    def __init__(self):
        self.solution_name = self.__class__.__name__
        self.categories = self.load_categories('../Categories.json')

    @abc.abstractmethod
    def process_document(self, filepath: str, filename: str, person_id: str) -> str:
        pass

    @staticmethod
    def load_categories(categories_filepath: str) -> List[Dict[str, Any]]:
        with open(categories_filepath, 'r') as file:
            categories_data = json.load(file)
        return categories_data['categories']

    def ingest_document(self, filepath: str, filename: str, person_id: str, request_data: bytes) -> str:
        try:
            print('REQUEST DATA')
            print(request_data)
            # Ensure the directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            # Write request data to the file
            with open(filepath, 'wb') as f:
                f.write(request_data)

            # Perform the processing
            document_labeled_text: str = self.process_document(filepath, filename, person_id)
            return document_labeled_text

        except Exception as e:
            # Log the exception if needed
            print(f"An error occurred: {e}")
            raise

        finally:
            # Cleanup temporary file
            if os.path.exists(filepath):
                os.remove(filepath)
                pass
