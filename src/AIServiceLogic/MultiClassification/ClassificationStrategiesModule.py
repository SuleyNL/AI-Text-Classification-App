from typing import Dict, List, Any
from abc import ABC, abstractmethod
from enum import Enum
from liqfit.pipeline import ZeroShotClassificationPipeline
from liqfit.models import T5ForZeroShotClassification
from transformers import T5Tokenizer


class ClassificationStrategy(ABC):
    category_list: List
    similarity_threshold: float

    def __init__(self, categories: List[Dict[str, Any]]):
        self.category_list = [category['name'] for category in categories]
        pass

    @abstractmethod
    def get_labels(self, sentence: str) -> List[str]:
        """
        [Mandatory inheritance function]

        Returns relevant categories for a given sentence based on embedding similarity
        and (optionally) matrix transformations performed by the embedder.

        Args:
            sentence (str): The input sentence.

        Returns:
            List[str]: A list of relevant theme names.
        """
        pass


class ComprehendIt(ClassificationStrategy):
    similarity_threshold = 0.6

    def __init__(self, categories):
        super().__init__(categories)

    def get_labels(self, sentence: str) -> List[str]:
        model = T5ForZeroShotClassification.from_pretrained('knowledgator/comprehend_it-multilingual-t5-base')
        tokenizer = T5Tokenizer.from_pretrained('knowledgator/comprehend_it-multilingual-t5-base')
        classifier = ZeroShotClassificationPipeline(model=model, tokenizer=tokenizer,
                                                    hypothesis_template='{}', encoder_decoder=True)

        similarities = classifier(sentence, self.category_list, multi_label=True)
        relevant_categories = []
        print(f"Sentence:")
        print("-" * 50)
        print(f"{sentence}")
        print("-" * 50)
        print("Theme similarities:")
        for category_name, similarity_score in zip(similarities['labels'], similarities['scores']):
            print(f"{category_name}: {similarity_score:.4f}")
            if similarity_score >= self.similarity_threshold:
                relevant_categories.append(category_name)

        print(f"Relevant themes: {relevant_categories}")
        print("-" * 50)

        return relevant_categories


class ClassificationStrategies(Enum):
    ComprehendIt = ComprehendIt

    @classmethod
    def _missing_(cls, value):
        raise ValueError(f"{value} is not a valid {cls.__name__}")

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        for name, value in cls.__members__.items():
            if not issubclass(value.value, ClassificationStrategy):
                raise TypeError(f"{name} must be a subclass of TransformationStrategy")

    def __call__(self, *args, **kwargs) -> ClassificationStrategy:
        return self.value(*args, **kwargs)


