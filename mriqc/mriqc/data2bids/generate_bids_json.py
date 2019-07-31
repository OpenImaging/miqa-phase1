#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 17:43:09 2019

@author: dhruv.sharma
"""

import json
import os

ALLOWED_MODALITIES = ["t2fse", "t1spgr", "mprage"]
#ALLOWED_MODALITIES = ["dti6b500pepolar", "t2fse", "dti30b400",
#                      "dti60b1000", "grefieldmap", "t1spgr",
#                      "rsfmri", "mprage"]

def get_BIDS_modality(modality):
    '''
    This function is to make the modality name as per the conventions of BIDS
    Args:
        modality : the original modality name as in the ALLOWED_MODALITIES
    Returns:
        the changed modality name as per BIDS naming conventions
        the modality type like 'anat', 'func', etc
    '''
    # TODO : inculcate the fMRIs in this module
    if (modality == 't1spgr' or modality == 'mprage'):
        return 'T1w', 'anat'
    if (modality == 't2fse'):
        return 'T2w', 'anat'
    return modality, 'etc'
    

def process_modality(sub_id, modality, modality_data, sub_data):
    '''
    This function generates the data for each session from the subject data
    for the modality provided.
    
    Args:
        sub_id : the subject id for getting the prefix in the name
        modality : the modality to which the data belongs to. It is one amongst
            the ones defined in ALLOWED_MODALITIES
        modality_data : the list of all session dictionaries corresponding to one modality
        sub_data : the dictionary of sessions to which the data is added.
    Returns:
        None
    '''
    
    # TODO : include the fMRI also to get their events.tsv
    bids_modality, modality_type = get_BIDS_modality(modality)
    if modality_type not in sub_data:
        sub_data[modality_type] = []
    for run in modality_data:
        run_id = run["run_id"]
        
        if(len(modality_data)==1):
            this_image_new_name = sub_id+'_'+bids_modality+'.nii.gz'
        else:
            this_image_new_name = sub_id+'_'+run_id+'_'+bids_modality+'.nii.gz'
    
        image_path = run["image_path"]
        
        image_dict = {}
        image_dict["new_name"] = this_image_new_name
        image_dict["image_path"] = image_path
        
        sub_data[modality_type].append(image_dict)
    

def process_one_subject(subject_data):
    '''
    processes one subject at a time and generates the data dictionary in a BIDS
    compatible form as explained in populate_bids_json:
        sub-0x -> ses-0x -> [anat -> {T1w, T2w} -> images, func -> {fmri} -> images, ...]
    
    Args:
        subject_data : all the processed data corresponding to one subject
    Returns:
        The subject data dictionary structured as explained above
    '''
    this_sub_id = subject_data["sub_id"]
    this_subject_data = {}
    for key in subject_data:
        if key in ALLOWED_MODALITIES:
            modality_data = subject_data[key]
            modality = key
            process_modality(this_sub_id, modality, modality_data, this_subject_data)
                
    return this_subject_data
        
def populate_bids_json(data):
    '''
    This function take the intermediary json generated and structures it to store
    data compatible with the BIDS format. It nests the dictoinary as follows:
        data -> sub-0x -> ses-0x -> [anat -> {T1w, T2w} -> images, func -> {fmri} -> images, ...]
    
    Args:
        data : intermediary json containing the processed data
    Return:
        bids_json : the dictionary containing the data in BIDS compatible format
    '''
    bids_json = {}
    for subject in data:
        this_sub = data[subject]
        this_sub_bids = process_one_subject(this_sub)
        if this_sub_bids:
            bids_json[subject] = this_sub_bids
                
    return bids_json

def main():
    intermediary_folder_path = './intermediate_files'
    inter_file_path = 'intermediary.json'
    with open(os.path.join(intermediary_folder_path, inter_file_path), 'r') as json_file:
        inter_file = json.load(json_file)

    bids_json = populate_bids_json(inter_file['data'])

    with open(os.path.join(intermediary_folder_path, "bids.json"), "w") as outfile:
       json.dump(bids_json, outfile, indent=4)    
    
if __name__ == '__main__':
    main()