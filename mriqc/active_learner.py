#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 09:38:23 2019

@author: dhruv.sharma
"""
import os

from model import Model
from data_loader import Data
from strategy import uncertainty_sampling
from glob import glob

def predict(path):
    '''
    This function forms the engine for the first part of MIQA and AL. This function
    helps in making the predictions for the new data that has been input.
    
    Args:
        path: path to the csv file with the new input data
    Returns:
        path: the new path to the file with the new input data
    '''
    # read the variables and data, load the model
    master_path = '/home/dhruv.sharma/Projects/MRIQC_AL/master_folder'#os.environ['MIQA_AL_PATH']
    
    weights_dir = 'saved_model'
    model_path = os.path.join(master_path, weights_dir)
    
    model = Model()
    new_data = Data(path)
    
    # if the model weights folder isn't there, make one
    if not os.path.isdir(model_path):
        os.mkdir(model_path)
    
    # if the model hasn't been trained yet, train it
    if(len(glob(os.path.join(model_path, '*.pkl'))) == 0):
        train()
    
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

def train(csv_path=None, on_new=False):
    '''
    This function ins the engine to train the model with the new data just labeled
    by the user of MIQA. The model can also be trained on the previously available
    labeled data.
    
    Args:
        csv_path: the path to the csv containing the newly labeled data
        on_new: if True will train on the new data as well, if False will train only
        on the available training data
    Returns:
        None
    '''
    # read the variables and data, load the model
    master_path = '/home/dhruv.sharma/Projects/MRIQC_AL/master_folder'#os.environ['MIQA_AL_PATH']
        
    weights_dir = 'saved_model'
    model_path = os.path.join(master_path, weights_dir)
    
    training_data_path = os.path.join(master_path, 'training_data.csv')
    training_data = Data(training_data_path)
    
    if not os.path.isdir(model_path):
        os.mkdir(model_path)
               
    if on_new:
        training_data_path = os.path.join(master_path, 'training_data.csv')
        training_data = Data(training_data_path)
        # load the data
        new_data = Data(csv_path)
        
        # get the query points
        idx, pred, _ = new_data.get_possible_query_points()
        query_idx = uncertainty_sampling(idx, good_preds=pred, n_instances=2)
        
        # extract the query points from data
        query_data = new_data.extract_query_points(query_idx)
        # add this new data to training_ data
        training_data.add_new_data(query_data)
        
        training_data.save()

    training_data_path = os.path.join(master_path, 'training_data.csv')
    training_data = Data(training_data_path)
    
    _, X, y = training_data.get_feature_and_labels()
    
    model = Model()
    model.fit(X, y)
    model.save_model(model_path)
    
if __name__ == '__main__':
    csv_path = '/home/dhruv.sharma/Projects/MRIQC_AL/mriqc_output.csv'
    decision_path = '/home/dhruv.sharma/Projects/MRIQC_AL/mriqc_output_decision_dummy.csv'
#    train(decision_path, on_new=True)
    predict(csv_path)
    
    
    
    