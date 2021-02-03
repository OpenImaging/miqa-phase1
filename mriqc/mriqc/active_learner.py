#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 09:38:23 2019

@author: dhruv.sharma
"""
import os
from glob import glob

from girder import logger

from .model_rf import ModelRF
from .data_loader import Data
from .strategy import uncertainty_sampling


def debug(msg):
    logger.info(msg)
    print(msg)


def predict(master_path, path, learningMode="randomForest"):
    '''
    This function forms the engine for the first part of MIQA and AL. This function
    helps in making the predictions for the new data that has been input.

    Args:
        master_path: the absolute path to the master folder with all important directories
        like training_data.csv, model_weights, log files
        path: path to the csv file with the new input data (must contain 'IQMs' col w/ quality metrics)
    Returns:
        path: the new path to the file with the new input data
    '''
    # read the variables and data, load the model
    weights_dir = 'saved_model'
    model_path = os.path.join(master_path, weights_dir)

    model = ModelRF()
    new_data = Data(path)

    # if the model weights folder isn't there, make one
    if not os.path.isdir(model_path):
        os.mkdir(model_path)

    # if the model hasn't been trained yet, train it
    if(len(glob(os.path.join(model_path, '*.pkl'))) == 0):
        train(master_path)

    # load the most recently saved model
    model.load_model(model_path)

    # get the features of the new data
    X_new_sub_ids, X_new_features = new_data.get_features()

    # make predictions
    X_new_preds = model.predict_proba(X_new_features)

    # add these predictions to the csv
    new_data.set_predictions(X_new_sub_ids, X_new_preds)

    # save the predictions to the csv
    new_data.save()

    return path

def train(master_path, csv_path=None, learningMode="randomForest"):
    '''
    This function ins the engine to train the model with the new data just labeled
    by the user of MIQA. The model can also be trained on the previously available
    labeled data.

    Args:
        master_path: the absolute path to the master folder with all important directories
        like training_data.csv, model_weights, log files
        csv_path: the path to the csv containing the newly labeled data
    Returns:
        None
    '''
    # read the variables and data, load the model

    weights_dir = 'saved_model'
    model_path = os.path.join(master_path, weights_dir)

    training_data_path = os.path.join(master_path, 'training_data.csv')
    training_data = Data(training_data_path)

    if not os.path.isdir(model_path):
        os.mkdir(model_path)

    if csv_path is not None:
        training_data_path = os.path.join(master_path, 'training_data.csv')
        training_data = Data(training_data_path)
        # load the data
        new_data = Data(csv_path)

        # get the query points
        # debug('Going to get possible query points')
        idx, pred, _ = new_data.get_possible_query_points()
        query_idx = uncertainty_sampling(idx, good_preds=pred, n_instances=2)

        # extract the query points from data
        # debug('Going to extract query points')
        query_data = new_data.extract_query_points(query_idx)
        # debug(query_data)

        # add this new data to training_ data
        # debug('Going to add new query data to existing data')
        training_data.add_new_data(query_data)
        # debug(training_data)

        # debug('Going to save updated training data')
        training_data.save()

    # load the (updated) training data and get the features and labels
    training_data_path = os.path.join(master_path, 'training_data.csv')
    # debug('Going to read training data in again {0}'.format(training_data_path))
    training_data = Data(training_data_path)

    # debug('Going to get features and labels')
    _, X, y = training_data.get_feature_and_labels()
    # debug('Got features and labels')

    # debug('got features')
    # debug(X)
    # debug('got labels')
    # debug(y)

    # upload the model and fit over the dataset
    model = ModelRF()
    model.fit(X, y)
    model.save_model(model_path)

    # update the predictions for the new data with the newly trained model
    if csv_path is not None:
        return predict(master_path, csv_path)

if __name__ == '__main__':
    master_path = '/Users/scott/miqa/larger_subset'
    # csv_path = '/Users/scott/miqa/larger_subset/scans_to_review_output.csv'
    decision_path = '/Users/scott/miqa/larger_subset/scans_to_review_output.csv'

    train(master_path, decision_path)
#    predict(master_path, csv_path)



