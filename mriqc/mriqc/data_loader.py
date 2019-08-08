#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 25 18:22:44 2019

@author: dhruv.sharma
"""

import pandas as pd

class Data():
    '''
    This class is to handle all the operations related to the data in the MIQA platform.
    It considers the CSV file as the main input and manipulates it only, assuming that
    the paths to the data is static. The state of the data changes at many occasions
    throughout its course of the MIQA. I have tried to handle all those cases independently
    
    This class loads the data and maintains it as a class variable which is a Pandas dataframe.
    Args:
        csv_path: The input it takes is the absolute path to the CSV file with the data.
    
    '''
    def __init__(self, csv_path):
        self.path = csv_path
        self.data = pd.read_csv(self.path)
    
    def save(self, path=None):
        '''
        This function overwrites the current csv file with the data it has till now.
        
        Args:
            path: path to save the file
        Returns:
            None
        '''
        if path==None:
            self.data.to_csv(self.path, index = False)
        else:
            self.data.to_csv(path, index = False)
    
    def _extract_iqm(self, iqms):
        '''
        A helper function to extract the list of IQMs from the string format
        
        Args:
            iqms: a string containing th IQM key and value pairs
        Returns:
            iqm_vals: a list of the IQM values in float type
        '''
        iqm_vals = []
        iqms = iqms.split(';')[:-1]
        for iqm in iqms:
            label, val = iqm.split(':')
            val = float(val)
            iqm_vals.append(val)
        return iqm_vals
        
    def get_features(self):
        '''
        This function is to access the IQM featueres for the available dataset
        
        Args:
            None
        Returns:
            sub_ids: The subjects for which the IQMs are available
            features: a list of IQMs for each of the subjects in sub_ids
        '''
        
        row_count = self.data.shape[0]
        features = []
        sub_ids = []
        
        for i in range(row_count):
            sub_id = self.data["xnat_experiment_id"][i]
            scan_type = self.data["scan_type"][i]
            iqm = self.data["IQMs"][i]
            if(type(iqm)!=type(0.0)):
                iqms = self._extract_iqm(iqm)
                sub_ids.append((sub_id,scan_type))
                features.append(iqms)
        
        return sub_ids, features
    
    def set_predictions(self, sub_ids, predictions):
        '''
        This function is to set the predictions corresponding to the subjects for
        which we have the predictions and update the current dataframe
        
        Args:
            sub_ids: The a list of tuples (subject, scan type) for which the IQMs are available
            predictions: the list of probabilities of the images being good
        Returns:
            None
        '''
        if 'good_prob' not in list(self.data.columns.values):
            self.data['good_prob'] = None
        
        row_count = self.data.shape[0]
        for i in range(row_count):
            sub_id = self.data['xnat_experiment_id'][i]
            scan_type = self.data['scan_type'][i]
            if((sub_id, scan_type) in sub_ids):
                ind = sub_ids.index((sub_id, scan_type))
                self.data['good_prob'][i] = predictions[ind]
        
    def get_feature_and_labels(self):
        '''
        This function is to extract the features and the labels for the data points
        
        Args:
            None
        Returns:
            sub_ids: The subjects for which the IQMs are available
            features: a list of IQMs for each of the subjects in sub_ids
            labels: a list of the labels corresponding to the subjects
        '''
        row_count = self.data.shape[0]
        features = []
        sub_ids = []
        labels = []
        
        for i in range(row_count):
            sub_id = self.data["xnat_experiment_id"][i]
            scan_type = self.data["scan_type"][i]
            iqm = self.data["IQMs"][i]
            if(type(iqm)!=type(0.0)):
                try:
                    if(self.data['decision'][i] == 1 or self.data['decision'][i] == 2):
                        iqms = self._extract_iqm(iqm)
                        sub_ids.append((sub_id,scan_type))
                        features.append(iqms)
                        labels.append(1)
                    elif(self.data['decision'][i] == -1):
                        iqms = self._extract_iqm(iqm)
                        sub_ids.append((sub_id,scan_type))
                        features.append(iqms)
                        labels.append(0)
                except:
                    print("subject", sub_id, "decision", self.data.decision[i])
        
        return sub_ids, features, labels
    
    def get_possible_query_points(self):
        '''
        This function extracts the indices of the data points which have predictions
        and returns a list of their indices and their predictions.
        
        Args:
            None
        Returns:
            indices: a list of the index of the data points which have predictions made.
            
            preds: the predictions for the image being good quality.
            
            features: the features of the input data, would be useful for batch-mode sampling.
        '''
        indices = []
        preds = []
        features = []
        row_count = self.data.shape[0]
        
        for i in range(row_count):
            if(self.data["good_prob"][i]!= None and type(self.data.IQMs[i])!=type(0.0)):
                indices.append(i)
                preds.append(self.data.good_prob[i])
                features.append(self._extract_iqm(self.data.IQMs[i]))
        
        return indices, preds, features
    
    def extract_query_points(self, indices):
        '''
        This function extracts the query points from the data and returns this subset
        dataframe with all its attributes
        
        Args:
            indices: the indices corresponding to the query points
        Returns:
            query_data: a subset of the original dataframe with all the data info
        '''
        return self.data.loc[indices]
    
    def add_new_data(self, new_data):
        '''
        This function is to add new data to the current data. basically for the main
        training data CSV.
        
        Args:
            new_data: a Dataframe containing the new data info
        Returns:
            None
        '''
        if(new_data.shape[0]!=0):
            ind = ~ new_data.xnat_experiment_id.isin(self.data.xnat_experiment_id) & new_data.scan_type.isin(self.data.scan_type)
            new_data = new_data.drop(columns = ['good_prob'])
            self.data = self.data.append(new_data[ind])
                
                
                