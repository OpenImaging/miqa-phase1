#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 25 17:37:09 2019

@author: dhruv.sharma
"""

from sklearn.ensemble import RandomForestClassifier
import joblib

from girder import logger
from datetime import datetime
import os
import glob

class Model():
    '''
    This class defines the model that we'll be using for our image quality prediction task.
    To start with, we are using Random Forest classifier. But, this is flexible and can be
    changed for future purposes by defining a new model and making suitable changes to the
    functions to make them compatible to the new model.

    Args:
        n_estimators: The number of classifiers in the RandomForest
    '''

    def __init__(self, n_estimators=30):
        self.model = RandomForestClassifier(n_estimators=n_estimators, max_features=5)

    def fit(self, X, y):
        '''
        This function is to fit the data to the model.

        Args:
            X: features of the data to be fit
            y: the true labels
        Returns:
            None
        '''
        # logger.info('Inside model.fit')
        # logger.info('features')
        # logger.info(X)
        # logger.info('labels')
        # logger.info(y)

        self.model.fit(X, y)

    def predict_proba(self, X):
        '''
        This function is to predict the probabilities of the input the data.

        Args:
            X: data to be predicted
        Returns:
            prob_good: array for the probabilities of data point being good
        '''
        predictions = self.model.predict_proba(X)
        return predictions[:,1]

    def save_model(self, model_path):
        '''
        This function saves the trained model in the given path

        Args:
            model_path: The path where the model needs to be saved
        Returns:
            None
        '''
        if not os.path.isdir(model_path):
            os.mkdir(model_path)

        file_name = os.path.join(model_path, 'rfc_'+datetime.now().strftime("%Y%m%d-%H%M%S")+'.pkl')
        joblib.dump(self.model, file_name)

    def load_model(self, model_path):
        '''
        This function loads the most recently saved trained model in the given path

        Args:
            model_path: The path where the model needs to be saved
        Returns:
            None
        '''
        saved_models = glob.glob(os.path.join(model_path, '*.pkl'))
        chckpt = max(saved_models, key=os.path.getctime)
        model = joblib.load(chckpt)
        self.model = model

