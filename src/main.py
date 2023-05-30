import pandas as pd
import numpy as np
import collections
import tensorflow as tf
import tensorflow_recommenders as tfrs
from tensorflow.keras.metrics import MeanAbsoluteError, RootMeanSquaredError, MeanSquaredError
import sklearn
from matplotlib import pyplot as plt
from typing import Dict, Text

movies_path = '../dataset/movies_metadata.csv'
rating_path = '../dataset/ratings_small.csv'

df_movies = pd.read_csv(movies_path).drop([19730, 29503, 35587])
df_rating = pd.read_csv(rating_path)

df_movies_cleaned = df_movies[['id', 'original_title']]
df_rating_cleaned = df_rating[['movieId', 'userId', 'rating']]
display(df_movies_cleaned.head(5))
display(df_rating_cleaned.head(5))
df_movies_cleaned['id'] = df_movies_cleaned['id'].astype('int64')

df_movies_cleaned.loc[:, 'id'] = pd.to_numeric(df_movies_cleaned['id'], errors='coerce').astype('Int64')
df_movies_cleaned = df_movies_cleaned.dropna(subset=['id']) # remove any line with NaN
display(df_movies_cleaned.head(5))

merged_dataset = pd.merge(df_rating_cleaned, df_movies_cleaned[['id', 'original_title']], left_on='movieId', right_on='id', how='left')

merged_dataset = merged_dataset[~merged_dataset['id'].isna()]
merged_dataset.dropna(inplace=True)
merged_dataset.drop('movieId', axis=1, inplace=True)
display(merged_dataset['id'].describe())
dataset_size = merged_dataset.shape[0] # count final size for dataset

merged_dataset.reset_index(drop=True, inplace=True)

display(merged_dataset.head())

df_movies_cleaned = df_movies_cleaned[~df_movies_cleaned['original_title'].duplicated()]
df_movies_cleaned['original_title'].head()

merged_dataset['userId'] = merged_dataset['userId'].astype(str)
# df_movies_cleaned['original_title'] = df_movies_cleaned['original_title'].astype(str)

rating_dict = dict(merged_dataset[['userId', 'original_title', 'rating']])
movies_dict = dict(df_movies_cleaned[['original_title']])

# Transfer to tf.tensor_slice
ratings_tf = tf.data.Dataset.from_tensor_slices(rating_dict)
movies_tf = tf.data.Dataset.from_tensor_slices(movies_dict)

movies_tf = movies_tf.map(lambda x: x["original_title"])

ratings_tf = ratings_tf.map(lambda x: {
    "original_title": x["original_title"],
    "rating": float(x["rating"]),
    "userId": x["userId"]
})
def slice_df_data(data_tf, total_size, test_rate=0.2):
    test_size = int(total_size * test_rate)
    train_size = total_size - test_size
    return data_tf.take(train_size), data_tf.skip(train_size).take(test_size)

train_ds, test_ds = slice_df_data(ratings_tf, dataset_size)
usrID_lookup = np.unique(np.concatenate([merged_dataset['userId'].to_numpy()]))
title_lookup = np.unique(np.concatenate([df_movies_cleaned['original_title']]))