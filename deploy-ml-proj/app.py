from flask import Flask, request, render_template
# import pickle

import os
import logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# from wordcloud import WordCloud
import random
import pandas as pd
import numpy as np
import tensorflow as tf
import tensorflow_recommenders as tfrs
from tensorflow.keras.metrics import MeanAbsoluteError, RootMeanSquaredError, MeanSquaredError
import sklearn
from matplotlib import pyplot as plt
from typing import Dict, Text

tf.get_logger().setLevel('ERROR')
# tf.logging.set_verbosity(tf.logging.ERROR)
logging.getLogger('tensorflow').setLevel(logging.FATAL)

app = Flask(__name__)

def slice_df_data(data_tf, total_size, test_rate=0.2):
        test_size = int(total_size * test_rate)
        train_size = total_size - test_size
        return data_tf.take(train_size), data_tf.skip(train_size).take(test_size)

# customized model for collaborative-based system
class CollabModel(tfrs.models.Model):
  def __init__(self, rating_w, retrieval_w, embedding_dim=64, L1_num=256, L2_num=128, L3_num=32, act_func="relu") -> None:
    super().__init__()
    embedding_dim = embedding_dim # number of dimension for embedding

    self.movie_model: tf.keras.layers.Layer = tf.keras.Sequential([
      tf.keras.layers.StringLookup(
        vocabulary=title_lookup, mask_token=None),
      tf.keras.layers.Embedding(len(title_lookup) + 1, embedding_dim)
    ])
    self.user_model: tf.keras.layers.Layer = tf.keras.Sequential([
      tf.keras.layers.StringLookup(
        vocabulary=usrID_lookup, mask_token=None),
      tf.keras.layers.Embedding(len(usrID_lookup) + 1, embedding_dim)
    ])
    self.rating_model = tf.keras.Sequential([
        tf.keras.layers.Dense(L1_num, activation=act_func), # first layer
        tf.keras.layers.Dense(L2_num, activation=act_func), # second layer
        tf.keras.layers.Dense(L3_num, activation=act_func),# third layer
        tf.keras.layers.Dense(1), # output layer
    ])

    self.rating_eval: tf.keras.layers.Layer = tfrs.tasks.Ranking(
        loss = MeanSquaredError(),
        metrics = [RootMeanSquaredError(), MeanAbsoluteError()],
    )
    self.retrieval_eval: tf.keras.layers.Layer = tfrs.tasks.Retrieval(
        metrics=tfrs.metrics.FactorizedTopK(
            candidates=movies_tf.batch(128).map(self.movie_model)
        )
    )

    self.rating_weight = rating_w
    self.retrieval_weight = retrieval_w

  # overloading call function
  def call(self, features: Dict[Text, tf.Tensor]) -> tf.Tensor:
    user_embeddings = self.user_model(features["userId"])
    movie_embeddings = self.movie_model(features["original_title"])
    
    return (
        user_embeddings,
        movie_embeddings,
        self.rating_model(
            tf.concat([user_embeddings, movie_embeddings], axis=1)
        ),
    )

  # overloading compute_loss function
  def compute_loss(self, features: Dict[Text, tf.Tensor], training=False) -> tf.Tensor: 
    label_r = features.pop("rating")
    user_embeddings, movie_embeddings, rating_pred = self(features)
    rating_loss = self.rating_eval(labels=label_r, predictions=rating_pred)
    retrieval_loss = self.retrieval_eval(user_embeddings, movie_embeddings)

    return (self.rating_weight * rating_loss
            + self.retrieval_weight * retrieval_loss)

movies_path = '../dataset/movies_metadata.csv'
rating_path = '../dataset/ratings_small.csv'
df_movies = pd.read_csv(movies_path).drop([19730, 29503, 35587])
df_rating = pd.read_csv(rating_path)
df_movies_cleaned = df_movies[['id', 'original_title']]
df_rating_cleaned = df_rating[['movieId', 'userId', 'rating']]
df_movies_cleaned['id'] = df_movies_cleaned['id'].astype('int64')
df_movies_cleaned.loc[:, 'id'] = pd.to_numeric(df_movies_cleaned['id'], errors='coerce').astype('Int64')
df_movies_cleaned = df_movies_cleaned.dropna(subset=['id']) # remove any line with NaN
merged_dataset = pd.merge(df_rating_cleaned, df_movies_cleaned[['id', 'original_title']], left_on='movieId', right_on='id', how='left')
merged_dataset = merged_dataset[~merged_dataset['id'].isna()]
merged_dataset.dropna(inplace=True)
merged_dataset.drop('movieId', axis=1, inplace=True)
dataset_size = merged_dataset.shape[0] # count final size for dataset
merged_dataset.reset_index(drop=True, inplace=True)
df_movies_cleaned = df_movies_cleaned[~df_movies_cleaned['original_title'].duplicated()]
merged_dataset['userId'] = merged_dataset['userId'].astype(str)
rating_dict = dict(merged_dataset[['userId', 'original_title', 'rating']])
movies_dict = dict(df_movies_cleaned[['original_title']])
ratings_tf = tf.data.Dataset.from_tensor_slices(rating_dict)
movies_tf = tf.data.Dataset.from_tensor_slices(movies_dict)
movies_tf = movies_tf.map(lambda x: x["original_title"])
ratings_tf = ratings_tf.map(lambda x: {
    "original_title": x["original_title"],
    "rating": float(x["rating"]),
    "userId": x["userId"]
})
train_ds, test_ds = slice_df_data(ratings_tf, dataset_size)
usrID_lookup = np.unique(np.concatenate([merged_dataset['userId'].to_numpy()]))
title_lookup = np.unique(np.concatenate([df_movies_cleaned['original_title']]))
model = CollabModel(rating_w=1.0, retrieval_w=1.0, embedding_dim=64, L1_num=256, L2_num=128, L3_num=32, act_func="relu")
model.compile(optimizer=tf.keras.optimizers.Adagrad(0.2))
train_ds_cache = train_ds.shuffle(10_000).batch(1_000).cache()
test_ds_cache = test_ds.batch(1_000).cache()
history = model.fit(train_ds_cache, epochs=1)

movies = tf.data.Dataset.from_tensor_slices(dict(df_movies_cleaned[['original_title']]))
movies = movies.map(lambda x: x["original_title"])

index = tfrs.layers.factorized_top_k.BruteForce(model.user_model)
# recommends movies out of the entire movies dataset.
index.index_from_dataset(
  tf.data.Dataset.zip((movies.batch(100), movies.batch(100).map(model.movie_model)))
)

index_M = tfrs.layers.factorized_top_k.BruteForce(model.movie_model)
# recommends movies out of the entire movies dataset.
index_M.index_from_dataset(
  tf.data.Dataset.zip((movies.batch(100), movies.batch(100).map(model.movie_model)))
)

def get_recommend(usrID, showRating):
  _, titles = index(tf.constant([usrID]))
  pred_movies = pd.DataFrame({'original_title': [i.decode('utf-8') for i in titles[0,:5].numpy()]}).to_numpy()
  return pred_movies

def M_get_recommend(movie_titles, showRating):
  _, titles = index_M(tf.constant([movie_titles]))
  pred_movies = pd.DataFrame({'original_title': [i.decode('utf-8') for i in titles[0,:5].numpy()]}).to_numpy()
  return pred_movies

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/recommend',methods=['POST'])
def recommend():
    """Grabs the input values and uses them to make recommendation"""
    user_id = request.form["userID"]
    recommendations = get_recommend(user_id, False)
    
    return render_template('result_user.html', recommendation_text=f'Recommendations for user {user_id}: {recommendations}')

@app.route('/recommend_Movie',methods=['POST'])
def recommend_Movie():
    """Grabs the input values and uses them to make recommendation"""
    movie_T = request.form["movie_T"]
    print(movie_T)
    recommendations_M = M_get_recommend(movie_T, False)
    
    return render_template('result_movie.html', recommendation_text=f'Recommendations for Movie {movie_T}: {recommendations_M}')


if __name__ == "__main__":
    app.run()
