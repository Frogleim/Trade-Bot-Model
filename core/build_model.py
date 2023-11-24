from sklearn.linear_model import LinearRegression
import numpy as np
from joblib import dump, load

import os

model_filename = 'linear_regression_model.joblib'
model_path = f'./model/{model_filename}'

if os.path.exists(model_path):
    model = load(model_path)
else:
    model = LinearRegression()


def train_model(X, y):
    # Fit the model with the new data
    model.fit(np.array(X).reshape(-1, 2), np.array(y).ravel())


def predict_price_change(X):
    # Reshape the input to a 2D array
    X_2d = np.array(X).reshape(1, -1) if len(X) == 1 else np.array(X).reshape(-1, 2)

    # Predict the price change based on the model
    return model.predict(X_2d)


X, y = [], []
price_change_prediction = [0.0]  # Initialize with a float

current_price = 2002.8
trading_range = 15.632
features = [[current_price, trading_range]]  # Wrap the features in a list

if hasattr(model, 'coef_') and model.coef_ is not None:
    price_change_prediction = predict_price_change(features)
    print("Price Change Prediction:", price_change_prediction)

X.append(features[0])  # Extract the inner list
y.append(price_change_prediction[0])
train_model(X, y)  # Update the model with new data
dump(model, model_path)  # Save the model to disk
