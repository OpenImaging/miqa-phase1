#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 11:58:18 2019

@author: dhruv.sharma
"""
import os
import csv
from glob import glob
import json
import argparse

'''
python restructure_files.py --csv '/home/dhruv.sharma/Projects/MRIQC_AL/miqa sample data/sample data new/scans_to_review-2019-01-23.csv'
--root '/home/dhruv.sharma/Projects/MRIQC_AL/miqa sample data/sample data new/datasnap-2019-01-23'
'''


def get_csv_contents(file_path):
    '''
    Reads the csv file and returns a list of rows split at comma. This csv file
    contains the path to the various scans, along with their unique experiment IDs.
    
    Args:
        file_path : path for the csv file
    
    Returns:
        list of lists : content of the row split on comma
    '''
    data = []
    with open(file_path, 'r') as csv_file:
        csvReader = csv.reader(csv_file, delimiter = ',')
#        next(csvReader)
        header = None
        for row in csvReader:
            if header is None:
                header = row
            else:
                data.append(row)
    
    return header,data
        
def group_by_subject(list_of_scans):
    '''
    Groups the data by experiment ID so that scans for a single subject are all 
    together, segregated by the unqie scan ID for each subject
    
    Args:
        list_of_scans : all scans stored as list of lists, i.e., raw csv content
    
    Returns:
        dictionary : each key corresponds to a subject, which stores the csv rows
                     associated with it
    '''
    subject_wise = {}
    for row in list_of_scans:
        scan_id = row[0]
        sub_id = scan_id.split('_')[-1]
        if sub_id not in subject_wise:
            subject_wise[sub_id] = [row]
        else:
            subject_wise[sub_id].append(row)
    
    return subject_wise

def get_initial_dict(name = "Project", License = "ABC", funding = ["UVW", "XYZ"], 
                     refs_and_links = ["paper1", "paper2"], DatabaseDOI = "mm/dd/yyyy", 
                     authors = ["author1", "author2", "author3"], 
                     bids_version="1.0.2", ):
    '''
    Generate the initial dictionary containing the basic information required to 
    generate the dataset_description.json
    
    Args:
        "Name": Put the name of your experiment here,
        "BIDSVersion": "1.0.2" or the version you are using,
        "License": License under which your data is distributed,
        "Authors": ["Author1", "Author2", "Author3", "etc."],
        "funding": ["Put your funding sources here", "as a list"],
        "refs_and_links": ["e.g. data-paper", "(methods-)paper", "etc."],
        "DatasetDOI": DOI of dataset (if there is one)
    
    Returns:
        a dictionary containing the basic data description
    '''
    data_dict = {}
    data_dict["dataset_description"] = {}
    data_dict["dataset_description"]["Name"] = name
    data_dict["dataset_description"]["License"] = License
    data_dict["dataset_description"]["Funding"] = funding
    data_dict["dataset_description"]["ReferencesAndLinks"] = refs_and_links
    data_dict["dataset_description"]["DatasetDOI"] = DatabaseDOI
    data_dict["dataset_description"]["Authors"] = authors
    data_dict["dataset_description"]["BIDSVersion"] = bids_version
    
    return data_dict

def _segregate_by_session(sub_id, path_to_sessions):
    '''
    This function segregates the multiple scans for a single subject within 
    the same folder into sessions, one for each scan
    Args:
        sub_id : the id of the subject with the prefix 'sub-'
        path_to_sessions : absolute paths to all the scans for a subject
    Returns:
        a list of dictionaries, each element correspondig to one session. Each 
        session dictionary stores the session ID and the absolute path to the 
        session scan
    '''
    sessions_list = []
    
    if len(path_to_sessions) == 0:
        print('No nii.gz files found for ', sub_id)
        return sessions_list
    
    elif len(path_to_sessions) == 1:
        this_session = {}
        this_session['run_id'] = 'run-01'
        this_session['image_path'] = path_to_sessions[0]
        sessions_list.append(this_session)
        return sessions_list
    
    for path in path_to_sessions:
        this_session = {}
        session_id = os.path.basename(path).split('.')[0][5:]
        this_session['run_id'] = 'run-'+session_id
        this_session['image_path'] = path
        sessions_list.append(this_session)
    
    return sessions_list
        

def add_one_subject(data_dict, subject_id, subject_data, root_path):
    '''
    Adds one subject at a time to the data_dict, segregating the scans on the
    basis of the modality and the session.
    
    Args:
        data_dict : the dictionary that contains all the processed dataset
        subject_id : scan_ID or the experiment ID unique to each subject
        subject_data : the csv rows corresponding to each subject
        root_path : absolute path to the the dataset folder
    '''
    
    new_sub_id_key = 'sub-'+str(subject_id)
    subject_dict = {}
    subject_dict['sub_id'] = new_sub_id_key
    subject_dict['experiment_id'] = subject_id
    
    for scan in subject_data:
        #'.../RESOURCES/nifti/11_ncanda-dti30b400-v1/
        scan_path = scan[1] + '/' + scan[2] + '_' + scan[3] + '/'
        
        #ncanda-dti30b400-v1 => dti30b400
        modality = scan[3].split('-')[1]
        sessions_this_modality = sorted(glob(root_path+scan_path+'*.nii.gz'))
        subject_dict[modality] = _segregate_by_session(new_sub_id_key, sessions_this_modality)
        
    data_dict['data'][new_sub_id_key] = subject_dict
        
    
def add_subject_data(data_dict, all_subject_data, root_path):
    '''
    Adds the subject data to the data_dict. Each subject will contain the root
    path to their folder, scans segregated by their modalities, and each modality 
    will have scans segregated by their sessions
    
    Args:
        data_dict : the dictionary that contains all the processed dataset
        all_subject_data : dictionary containing the data grouped by each subject
        root_path : absolute path to the the dataset folder
    
    Returns:
        None    
    '''
    
    data_dict['data'] = {}
    
    for subject in all_subject_data:
        add_one_subject(data_dict=data_dict, subject_id=subject,
                        subject_data=all_subject_data[subject],
                        root_path=root_path)
    

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-c", "--csv", required=True,
                    help = "path to the csv file")
    ap.add_argument("-r", "--root", required=True,
                    help = "absolute path to the image root folder")
    args = vars(ap.parse_args())
    
    csv_path = args["csv"]#'/home/dhruv.sharma/Projects/MRIQC_AL/miqa sample data/sample data new/scans_to_review-2019-01-23.csv'
    root_path = args["root"]#'/home/dhruv.sharma/Projects/MRIQC_AL/miqa sample data/sample data new/datasnap-2019-01-23'
    intermediary_file_path = './intermediate_files'
    
    _, csv_content = get_csv_contents(csv_path)
    subject_wise_data = group_by_subject(csv_content)
#    print(subject_wise_data['E08706'])
    
    data_dict = get_initial_dict()
    add_subject_data(data_dict=data_dict, 
                     all_subject_data=subject_wise_data,
                     root_path=root_path)
    
    if not os.path.isdir(intermediary_file_path):
        os.mkdir(intermediary_file_path)
        
    with open(os.path.join(intermediary_file_path,"intermediary.json"), "w") as outfile:
        json.dump(data_dict, outfile, indent=4)

    
if __name__ == '__main__':
    main()
    

