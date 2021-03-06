import os
import numpy as np
import pandas as pd
from sklearn import metrics
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import lightgbm
import joblib

def split_data(data_df): # NOQA: E302, E261
    """Split a dataframe into training and validation datasets"""
    features = data_df.drop(['target', 'id'], axis = 1) # NOQA: E251, E261
    labels = np.array(data_df['target'])
    features_train, features_valid, labels_train, labels_valid = train_test_split(features, labels, test_size=0.2, random_state=0) # NOQA: E501, E261

    train_data = lightgbm.Dataset(features_train, label=labels_train)
    valid_data = lightgbm.Dataset(features_valid, label=labels_valid, free_raw_data=False) # NOQA: E501, E261
    return (train_data, valid_data)


def train_model(data, parameters):
    """Train a model with the given datasets and parameters"""
    # The object returned by split_data is a tuple.
    # Access train_data with data[0] and valid_data with data[1]
    train_data = data[0]
    valid_data = data[1]
    model = lightgbm.train(parameters,
                           train_data,
                           valid_sets=valid_data,
                           num_boost_round=500,
                           early_stopping_rounds=20)
    return model


def get_model_metrics(model, data):
    """Construct a dictionary of metrics for the model"""
    train_data = data[0] # NOQA: F841, E261
    valid_data = data[1]
    predictions = model.predict(valid_data.data)
    fpr, tpr, thresholds = metrics.roc_curve(valid_data.label, predictions)
    mse = mean_squared_error(predictions, valid_data.label)
    model_metrics = {"auc": (metrics.auc(fpr, tpr))}
    model_metrics = {"mse": mse}
    return model_metrics


def main():
    """This method invokes the training functions for development purposes"""
    # Read data from a file
    data_df = pd.read_csv('porto_seguro_safe_driver_prediction_input.csv')

    # Hard code the parameters for training the model
    parameters = {
        'learning_rate': 0.02,
        'boosting_type': 'gbdt',
        'objective': 'binary',
        'metric': 'auc',
        'sub_feature': 0.7,
        'num_leaves': 60,
        'min_data': 100,
        'min_hessian': 1,
        'verbose': 2
    }

    # Call the functions defined in this file
    data = split_data(data_df)
    model = train_model(data, parameters)
    # Print the resulting metrics for the model
    get_model_metrics(model, data)

    output_folder = "output"
    os.makedirs(output_folder, exist_ok=True)
    output_path = output_folder + "/smitha_driver_model.pkl"
    print(output_path)
    joblib.dump(value=model, filename=output_path)


if __name__ == '__main__':
    main()
