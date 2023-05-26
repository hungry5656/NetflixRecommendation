# Documentation

## Question
### model input
- For now, our model is user to item system, which means that the input for our model is user id.
- Not sure if we should change it to item to item system (input a movie)
- When showing our demo, people may getting confused about why this model can only predict user in dataset
- possible solution:
- - give port to let user add their own data to the dataset, and retrain the model.
- - We display the historical rating for that user id, and we display the recommended movies to compare the difference. (This requires us to show the genre and description for movies)

### Are we allowed to use library like this (tensorflow-recommender)

### How can we evaluate model
- we haven't done hyperparameter tuning
- - should we consider using different optimizer? SGD, Momentum, 

### What type of graph is needed to evaluate our model
- We have RMSE and we are trying to add MAE (Mean Absolute Error)
