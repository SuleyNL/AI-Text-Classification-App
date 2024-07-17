
A potential solution is the [comprehend_it-multilingual-t5](https://huggingface.co/knowledgator/comprehend_it-multilingual-t5-base)

Here we use the [deberta](https://huggingface.co/docs/transformers/model_doc/deberta) base model.
It builds on RoBERTa with disentangled attention and enhanced mask decoder training with half of the data used in RoBERTa.

The variant of deberta we use is one that is made by Valerii Vasylevskyi and his team from [knowledgator.com](knowledgator.com)
using [this dataset](https://huggingface.co/datasets/knowledgator/events_classification_biotech)

This came to my attention through [this blog of Valerii Vasylevskyi](https://huggingface.co/blog/Valerii-Knowledgator/multi-label-classification), 
describing their process and how to finetune your own multi-classification model.

## Why this model
Importantly this model can perform Multi-class classification; meaning it can give a given sentence multiple labels. 
And it can do this zero-shot. The zero-shot classifier supports nearly 100 languages and can work in both directions, meaning that labels and text can belong to different languages.
Furthermore, it is easy to use;
```python
from liqfit.pipeline import ZeroShotClassificationPipeline
from liqfit.models import T5ForZeroShotClassification
from transformers import T5Tokenizer

model = T5ForZeroShotClassification.from_pretrained('knowledgator/comprehend_it-multilingual-t5-base')
tokenizer = T5Tokenizer.from_pretrained('knowledgator/comprehend_it-multilingual-t5-base')
classifier = ZeroShotClassificationPipeline(model=model, tokenizer=tokenizer,
                                                      hypothesis_template = '{}', encoder_decoder = True)

sequence_to_classify = "one day I will see the world"
candidate_labels = ['travel', 'cooking', 'dancing']
classifier(sequence_to_classify, candidate_labels, multi_label=False)
# OUTPUT:
# {'sequence': 'one day I will see the world',
#  'labels': ['travel', 'cooking', 'dancing'],
#  'scores': [0.7350383996963501, 0.1484801471233368, 0.1164814680814743]}
```

