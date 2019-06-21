#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 10:13:52 2019

@author: dhruv.sharma
"""

import json
import csv
import argparse
import os
from glob import glob

'''
python process_iqms.py -m ../../data2bids/mriqc_output/ -o ../../mriqc_output.csv
'''

def process_json_file(json_path):
    '''
    This function creates a dictionary for each json_file and returns the iqms and
    also the list of iqms.
    Args:
        json_path: path to the json file of the subject
    Returns:
        iqms: list of IQMs processed for each subject
        iqm_values: a dictionary, containing the iqms for the subject and 
                    some metadata 
    '''
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    iqms = list()
    iqm_values = dict()
    
    for k in data:
        if(k=="bids_meta"):
            iqm_values["subject_id"] = 'NCANDA_'+data[k]["subject_id"]
            iqm_values["modality"] = data[k]["modality"]
        elif(k!='provenance'):
            iqm_values[k] = data[k]
            iqms.append(k)
    
    return iqms, iqm_values
    

def process_modality_folder(modality_path):
    '''
    This function extracts the iqms for each modality folder, given the path to 
    the folder of the subject
    Args:
        subject_path: folder path to the subject
        
    Returns:
        iqms: list of IQMs processed for each subject
        iqm_values: a list of dictionaries(one for each scan), containing 
                    the iqms for the subject and some metadata
    '''
    iqms = set()
    iqm_values = []
    json_files = os.listdir(modality_path)
    for json_file in json_files:
        json_path = os.path.join(modality_path, json_file)
        this_iqm, this_iqm_vals = process_json_file(json_path)
        iqms.update(this_iqm)
        if(len(iqm_values)==0):
            iqm_values.append(this_iqm_vals)
        else:
            iqm_values = iqm_values + [this_iqm_vals]
        
    return iqms, iqm_values

def get_iqm_subject(subject_path):
    '''
    This function extracts the iqms for each subject, given the path to the folder
    of the subject
    Args:
        subject_path: folder path to the subject
        
    Returns:
        iqms: list of IQMs processed for each subject
        iqm_values: a list of dictionaries(one for each scan), containing 
                    the iqms for the subject and some metadata
    '''
    iqms = set()
    iqm_values = []
    modalities = os.listdir(subject_path)
    for mod in modalities:
        modality_path = os.path.join(subject_path, mod)
        mod_iqms, mod_iqm_vals = process_modality_folder(modality_path)       
        iqms.update(mod_iqms)
        iqm_values = iqm_values + mod_iqm_vals
    
    return iqms, iqm_values

def get_iqms(mriqc_output_path):
    '''
    This function is to extract all the IQMs for each subject from their 
    repective jsons.
    Args:
        mriqc_output_path: this defines the path where the MRIQC output is stored
    
    Returns:
        iqms: list of IQMs processed for each subject
        iqm_values: a list of dictionaries(one for each subject), containing 
                    the iqms for each subject and some metadata
    '''
    subject_folder_paths = glob(mriqc_output_path+'sub*/')
    iqms = set()
    iqm_values = []
    
    for subject in subject_folder_paths:
        sub_iqms, sub_iqms_vals = get_iqm_subject(subject)
        iqms.update(sub_iqms)
        iqm_values = iqm_values + sub_iqms_vals
    
    return sorted(list(iqms)), iqm_values

def generate_csv(csv_path, iqms, iqm_values):
    '''
    This function writes the iqm_values into the csv path, one row per subject.
    Args:
        csv_path: This is the path to the csv file where all the IQMs will be dumped.
        iqms: the list of iqms extracted
        iqm_values: The list of dictionary corresponding to each scan
    Returns:
        None
    '''
    header = ["subject_id", "modality"]
    header.extend(iqms)
    
    with open(csv_path, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for scan in iqm_values:
            metrics = []
            for k in header:
                metrics.append(scan[k])
            
            writer.writerow(metrics)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-m", "--mriqc_output_path", required=True,
                    help = "path to the MRIQC output directory")
    ap.add_argument("-o", "--csv_output_path", required=True,
                    help = "path to save the processed csv file")
    args = vars(ap.parse_args())
    
    mriqc_output = args["mriqc_output_path"]#"../../data2bids/mriqc_output/"
    csv_path = args["csv_output_path"]
    
    iqms, iqm_values = get_iqms(mriqc_output)
    generate_csv(csv_path, iqms, iqm_values)
        
if __name__ == '__main__':
    main()
    