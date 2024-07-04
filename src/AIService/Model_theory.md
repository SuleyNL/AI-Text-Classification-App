# Generated ideas and insights
## Doc2vec where each doc is a sentence.

This implementation of Doc2vec can have an  additional tag-vector for each of the themes. 
And then we can check the similarity of every unique document (sentence) to every tag,
https://medium.com/wisio/a-gentle-introduction-to-doc2vec-db3e8c0cce5e

> a specifically *dutch* doc2vec would be needed, as its performance is expected to drop when using unknown words for its language


## Efficient storage
Matryoshka embeddings can reduce the dimensionality of an embedding while containing most of its semantic meaning
This can be finetuned to our specific use-case.

Shortlisting and reranking: Rather than performing your downstream task (e.g., nearest neighbor search) on the full 
embeddings, you can shrink the embeddings to a smaller size and very efficiently "shortlist" your embeddings. 
Afterwards, you can process the remaining embeddings using their full dimensionality.
Trade-offs: Matryoshka models will allow you to scale your embedding solutions to your desired storage cost, 
processing speed, and performance

Even at 8.3% of the embedding size, the Matryoshka model preserves 98.37% of the performance,
https://huggingface.co/blog/matryoshka

> matryoshka version of your model should probably need to be trained, but as we have no training data it wont be usable

## Vector similarity Metrics
Squared L2 Distance: Choose this if you need to measure absolute differences in feature values and if the scale and 
magnitude of embeddings are important in your use case. It works well in scenarios where absolute positioning in the 
embedding space is crucial.

Inner Product: This is suitable if your embeddings' magnitudes carry meaningful information and you are interested in 
both the direction and magnitude of vectors. It is useful in recommendation systems and collaborative filtering.

Cosine Similarity: Opt for cosine similarity if the direction of vectors (indicating similarity in terms of angle) is 
more important than their magnitude. This is particularly useful in NLP applications where the goal is to measure 
semantic similarity between word embeddings or document vectors.

> Cosine Similarity I think is the best for our use-case where we mainly want the general direction of an embedding to 
be used as classification for one of the categories


## Alternative solution
All sentences into embeddings vector store.
Define search-words for each category
Search each word with cosine similarity, label all sentences higher than sensitivity_threshold with that category
Repeat for each word in each category.

##