import abc
import json
import os
import traceback
from typing import List, Dict, Any

from bs4 import BeautifulSoup


class AI_solution(abc.ABC):
    """
    Abstract base class for AI solutions.

    This class provides a framework for solutions that require the logic for processing documents and
    importing categories from the `src/Categories.json` file.

    Attributes:
        solution_name (str): The name of the AI solution (derived from class name).
        categories (List[Dict[str, Any]]): A list of category dictionaries loaded from a JSON file.
            Each category dictionary contains:
            - id (int): The unique identifier for the category.
            - name (str): The name of the category.
            - wordCloud (List[str]): A list of words associated with the category.
    """

    def __init__(self):
        """
        Initialize the AI_solution with a solution name and load categories from a JSON file.
        """
        self.solution_name: str = self.__class__.__name__
        self.categories: List[Dict[str, Any]] = self.load_categories('../Categories.json')

    @abc.abstractmethod
    def process_document(self, filepath: str, filename: str, person_id: int) -> str:
        """
        Abstract method to process a document.

        This method should be implemented by subclasses to define how a document
        is processed and analyzed.

        Args:
            filepath (str): The path to the document file.
            filename (str): The name of the document file.
            person_id (int): The ID of the person associated with the document.

        Returns:
            str: The processed document content, typically with category labels.
        """
        pass

    @staticmethod
    def load_categories(categories_filepath: str) -> List[Dict[str, Any]]:
        """
        Load categories from a JSON file.

        The JSON file should have a structure like:
        {
          "categories":
          [
            {
              "id": int,
              "name": str,
              "wordCloud": List[str]
            },
            ...
           ]
        }

        Args:
            categories_filepath (str): The path to the JSON file containing category data.

        Returns:
            List[Dict[str, Any]]: A list of category dictionaries, each containing
                                  'id', 'name', and 'wordCloud' keys.

        Raises:
            FileNotFoundError: If the categories file is not found.
            json.JSONDecodeError: If the JSON file is invalid.
            KeyError: If the "categories" key is missing from the JSON data.
        """
        try:
            with open(categories_filepath, 'r') as file:
                categories_data = json.load(file)
            return categories_data['categories']
        except FileNotFoundError:
            print(f"Categories file not found: {categories_filepath}")
            raise
        except json.JSONDecodeError:
            print(f"Invalid JSON in categories file: {categories_filepath}")
            raise
        except KeyError:
            print(f"Missing 'categories' key in JSON file: {categories_filepath}")
            raise

    def ingest_document(self, filepath: str, filename: str, person_id: int, request_data: bytes) -> str:
        """
        Ingest a document, save it temporarily, process it, and clean up (Delete it) afterwards.

        This method handles the full lifecycle of document ingestion, from
        saving the document, processing it, to removing the temporary file.
        # TODO make it truly a temp_file using the tempfile library

        Args:
            filepath (str): The path where the document will be temporarily saved.
            filename (str): The name of the document file.
            person_id (int): The ID of the person associated with the document.
            request_data (bytes): The binary content of the document.

        Returns:
            str: The processed document content with category labels.

        Raises:
            Exception: If any error occurs during the ingestion process.
        """
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
            print(f"An error occurred during document ingestion: {e}")
            traceback.print_exc()
            raise

        finally:
            # Cleanup temporary file
            if os.path.exists(filepath):
                os.remove(filepath)

    def get_category_id_by_name(self, name: str) -> int:
        """
        Get the ID of a category by its name.

        Args:
            name (str): The name of the category.

        Returns:
            int: The ID of the category.

        Raises:
            ValueError: If the category is not found.
        """
        for category in self.categories:
            if category["name"] == name:
                return category["id"]

        raise ValueError(f"Category '{name}' not found.")

    def extract_unique_categories(self, html_string: str) -> List[int]:
        """
        Extract unique category IDs from a HTML string.

        This method parses the HTML string and extracts unique category IDs
        from span elements with class names starting with 'cat'.

        Args:
            html_string (str): The HTML string containing category information.

        Returns:
            List[int]: A list of unique category IDs.
        """
        soup = BeautifulSoup(html_string, 'html.parser')
        unique_categories = set()

        for span in soup.find_all('span'):
            if 'class' in span.attrs:
                for cls in span.attrs['class']:
                    if cls.startswith('cat'):
                        cat_id = cls.replace('cat', '')
                        if cat_id:
                            unique_categories.add(int(cat_id))

        return list(unique_categories)
