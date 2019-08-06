#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 09:08:03 2019

@author: dhruv.sharma
"""

import numpy as np

def uncertainty_sampling(indices, good_preds, n_instances):
    '''
    This function finds the most uncertain n_instances from the good_preds and returns their indices
    
    Args:
        indices: the indices of the data points being considered from the original dataset
        good_preds: the probability of the image being good
    Returns:
        query_idx, a list of indices of the query points
    '''
    n_instances = min(n_instances, len(good_preds))
    
    good_preds = np.array(good_preds)
    bad_preds = 1 - good_preds
    
    preds = np.zeros((len(good_preds), 2))
    preds[:,0] = bad_preds
    preds[:,1] = good_preds
    
    uncertainty = 1 - np.max(preds, axis=1)
    
    max_idx = np.argpartition(-uncertainty, n_instances-1, axis=0)[:n_instances]
    query_idx = [indices[i] for i in max_idx]
    
    return query_idx