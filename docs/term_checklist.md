# Important Terminology

## Collaborative filtering
- the strategy we choose for our model
- useful link: https://developers.google.com/machine-learning/recommendation/collaborative/basics
- The feedback about movies falls into one of two categories(copied from the website above)
- - Explicit - users specify how much they liked a particular movie by providing a numerical rating.
- - Implicit - if a user watches a movie, the system infers that the user is interested.

## Embedding
- creating the embedding matrix for user/item, which has a size of $m \times n$. $m$ represent the size of unique user/item. $n$ represent the number of hidden attribute you set to help to identify the feedback matrix.
- using the api from tfrs to create embedding: tf.keras.layers.Embedding()

## Matrix factorization
- useful link: https://developers.google.com/machine-learning/recommendation/collaborative/matrix
- feedback matrix is calculated using the product of user embedding matrix and transpose of item embedding matrix ($UV^T$)
- training task: minimize the sum of squared errors

## Retrival model
- useful url: https://www.tensorflow.org/recommenders/examples/basic_retrieval
- using the api from tfrs: tfrs.metrics.FactorizedTopK, tfrs.tasks.Retrieval
- Implicit
- producing the 

## Rating model
- useful url: https://www.tensorflow.org/recommenders/examples/basic_ranking
- using the api from tfrs: tfrs.tasks.ranking
- Explicit
- 3 layer neural network
- first layer:256
- second layer: 128
- third layer: 32

## Model evaluation
- test on unseen data
- The test result are usually low because this is an unsupervised learning.

## weight for this two sub model
- rating_w = 1.0, retrieval_w = 0
- - 
- rating_w = 0, retrieval_w = 1.0
- - 
- rating_w = 1.0, retrieval_w = 1.0
- - 
