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
from data2bids.restructure_files import get_csv_contents
from data2bids.generate_bids_json import get_BIDS_modality
'''
python process_iqms.py -m ../../data2bids/mriqc_output/ -co ../../mriqc_output.csv -ci '/home/dhruv.sharma/Projects/MRIQC_AL/miqa sample data/sample data new/scans_to_review-2019-01-23.csv'
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
        elif(k!='provenance' and k!='summary_bg_n' and k!='summary_csf_n' and k!='summary_gm_n' and k!='summary_wm_n' and
             'spacing_' not in k and 'size_' not in k):
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

def get_id_mod(row):
    '''
    This function is to extract the experiment id and the modality for the subject
    Args:
        row: the data for the subject in csv
    Returns:
        id: the subject experiment ID
        modality: the processed modality
    '''
    sub_id = row[0]
    mod = row[3].split('-')[1]
    mod, _ = get_BIDS_modality(mod)
    return sub_id, mod

def input_csv_to_dict(csv_content):
    '''
    This function is to make a dictionary of the input csv file content so that it can
    be mapped to the IQMs lter using the experiment ID and the modality.
    Args:
        csv_content: A list of lists, where each list corresponds to the data 
                     for each subject
    Returns:
        A dictionary hashed on each experiment id, which is futher hashed on the
        modality
    '''
    csv_dict = dict()
    for row in csv_content:
        if len(row) == 4:
            row.append('')
            row.append('')
            row.append('')
        sub_id, mod = get_id_mod(row)
        if sub_id in csv_dict:
            csv_dict[sub_id][mod] = row
        else:
            csv_dict[sub_id] = {}
            csv_dict[sub_id][mod] = row
    
    return csv_dict

def iqms_to_dict(iqms, iqm_vals):
    '''
    This function converts the list of dictionaries for each IQM to a dictionary 
    mapped on the experiment ID and further on the modality
    Args:
        iqms_vals: the list of dictionaries processed to contain the iqms for each subject
        iqm: The list of IQMs as keys
    Returns:
        A dictionary hashed on each subject to contain the iqms
    '''
    iqm_dict = {}
    
    for scan in iqm_vals:
        sub_id = scan["subject_id"]
        modality = scan["modality"]
        
        iqm_col = ""
        for iqm in iqms:
            this_iqm = str(iqm)+':'+str("{0:.3f}".format(scan[iqm]))+';'
            iqm_col += this_iqm 
        
        if sub_id not in iqm_dict:
            iqm_dict[sub_id] = {}
        iqm_dict[sub_id][modality] = iqm_col
    
    return iqm_dict
    

def generate_csv(csv_opath, iqm_dict, csv_dict, header):
    '''
    This function maps the two dictionaries containing the data into a single list of lists
    Args:
        csv_opath: This is the path to the csv file where all the IQMs will be dumped
                    along with the other information for MIQA input.
        iqm_dict: A dictionary hashed on each subject to contain the iqms
        csv_dict: A dictionary hashed on each experiment id, which is futher hashed on the
                  modality
        header: The header to the csv file
    Returns:
        None
    '''
    header.append("IQMs")

    with open(csv_opath, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for exp_id in csv_dict:
            exp_dict = csv_dict[exp_id]
            for mod in exp_dict:
                row = exp_dict[mod]
                if exp_id in iqm_dict and mod in iqm_dict[exp_id]:
                    row.append(iqm_dict[exp_id][mod])
                writer.writerow(row)
            
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-m", "--mriqc_output_path", required=True,
                    help = "path to the MRIQC output directory")
    ap.add_argument("-co", "--csv_output_path", required=True,
                    help = "path to save the processed csv file")
    ap.add_argument("-ci", "--csv_input_path", required=True,
                    help = "path to original csv file to be fed to MIQA as input")
    args = vars(ap.parse_args())
    
    mriqc_output = args["mriqc_output_path"]#"../../data2bids/mriqc_output/"
    csv_opath = args["csv_output_path"]
    csv_ipath = args["csv_input_path"]
    
    iqms, iqm_values = get_iqms(mriqc_output)
    iqm_dict = iqms_to_dict(iqms, iqm_values)
    
    header, csv_data = get_csv_contents(csv_ipath)
    csv_dict = input_csv_to_dict(csv_data)
    
    
    
    generate_csv(csv_opath, iqm_dict, csv_dict, header)
            
if __name__ == '__main__':
    main()
    