#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 15:21:02 2019

@author: dhruv.sharma
"""
import os
import json
import shutil
import argparse

'''
python bidsify.py --output_dir "./bids_output"
'''

def generate_basic_files(bids_folder, data_description):
    '''
    This function creates the basic files necessary as per the BIDS requirements,
    like dataset_description.json and README file.
    
    ########### Sample dataset_description.json ###########
    {
        "Name": "Put the name of your experiment here",
        "BIDSVersion": "1.0.2",
        "License": "License under which your data is distributed",
        "Authors": ["Author1", "Author2", "Author3", "etc."],
        "Acknowledgements": "Put your acknowledgements here",
        "HowToAcknowledge": "Describe how you'd like to be acknowledged here",
        "Funding": "Put your funding sources here",
        "ReferencesAndLinks": ["e.g. data-paper", "(methods-)paper", "etc."],
        "DatasetDOI": "DOI of dataset (if there is one)"
    }
    ######################################################
    
    ########## Sample README file ########################
    This dataset was obtained from the OpenfMRI project (http://www.openfmri.org).
    Accession #: ds005
    Description: Mixed-gambles task
    
    Please cite the following references if you use these data:
    
    Tom, S.M., Fox, C.R., Trepel, C., Poldrack, R.A. (2007). The neural basis of loss aversion in decision-making under risk. Science, 315(5811):515-8
    
    
    Release history:
    10/06/2011: initial release
    3/21/2013: Updated release with QA information
    2/18/2016: Update orientation information in nifti header for improved left-right determination
    
    This dataset is made available under the Public Domain Dedication and License 
    v1.0, whose full text can be found at 
    http://www.opendatacommons.org/licenses/pddl/1.0/. 
    We hope that all users will follow the ODC Attribution/Share-Alike 
    Community Norms (http://www.opendatacommons.org/norms/odc-by-sa/); 
    in particular, while not legally required, we hope that all users 
    of the data will acknowledge the OpenfMRI project and NSF Grant 
    OCI-1131441 (R. Poldrack, PI) in any publications.
    #####################################################

    Args:
        bids_folder : the output folder path which contains the data in the BIDS format
        data_description : the information required for generating the dataset_description.json file
    Returns:
        None
    '''
    if not os.path.isdir(bids_folder):
        os.mkdir(bids_folder)
    with open(os.path.join(bids_folder, 'dataset_description.json'), 'w') as json_file:
        json.dump(data_description, json_file, indent=4)
        
    with open(os.path.join(bids_folder, 'README'), 'w') as txt_file:
        text = "This dataset was obtained from the mIQa tool.\nDescription: Image-Quality assesment."
        txt_file.write(text)

def bidsify_each_image(image_info, root_folder_path):
    '''
    This function processes each image and places in the BIDS folder. It renames the
    image as per the BIDS naming convention sub-xxx_[run-0x_][modality].nii.gz
    
    Args:
        image_info : the dictionary containing the information about thr image like:
            {
                "new_name": "sub-E08712_T1w.nii.gz", 
                "image_path": "/original/path/to/the/folder"
            }
        root_folder_path : this is the path to the modality folder within which
            the image needs to be placed
    Returns:
        None
    '''
    image_path_src = image_info["image_path"]
    image_name_src = os.path.basename(image_path_src)
    
    image_name_dst = image_info["new_name"]
    image_path_dst = os.path.join(root_folder_path, image_name_src)
    image_path_new = os.path.join(root_folder_path, image_name_dst)

    
    shutil.copy(image_path_src, root_folder_path)
    os.rename(image_path_dst, image_path_new)
    
    

# TODO : add functionality for fMRI
def bidsify_each_modality(modality, modality_images, root_folder_path):
    '''
    This function is to create the modality folde for the subject ad place files within in accordingly
    Args:
        modality : the modality required to name the folder
        modality_images : the list of images to be placed under this folder
        root_folder_path : this folder is the path to the subject in which the images are to be added
    Returns:
        None
    '''
    modality_folder_path = os.path.join(root_folder_path, modality)
    if not os.path.isdir(modality_folder_path):
        os.mkdir(modality_folder_path)
    else:
        print('\t', modality, " has already been bidsified")
        return
    
    for image in modality_images:
        bidsify_each_image(image, modality_folder_path)

def bidsify_each_subject(sub_id, sub_dict, root_bids_folder):
    '''
    This function is to generate the BIDS folder for one subject and the subdirectories within it
    
    Args:
        sub_id : the Subject ID which is needed to name the folder for each subject
        sub_dict : This dictionary contains all the images segregated by modality
        root_bids_folder : the folder within which the subject folder will be placed
    Returns:
        None
    '''
    print('Processing subject:', sub_id)
    subject_folder_name = sub_id
    subject_folder_path = os.path.join(root_bids_folder, subject_folder_name)
    
    if not os.path.isdir(subject_folder_path):
        os.mkdir(subject_folder_path)
    else:
        print(sub_id, " has already been bidsified")
        return
    
    for modality in sub_dict:
        modality_data = sub_dict[modality]
        bidsify_each_modality(modality, modality_data, subject_folder_path)
        

def bidsify_json(bids_folder, bids_json_file):
    '''
    This function is the engine to generate the BIDS directory structure using the
    information stored in the json file
    
    Args:
        bids_folder : the path to the folder in which the BIDS output will be placed
        bids_json_file : the json file with the data in BIDS compatible format
    Returns:
        None
    '''
    for subject in bids_json_file:
        sub_id = subject
        sub_dict = bids_json_file[sub_id]
        bidsify_each_subject(sub_id, sub_dict, bids_folder)
        
def is_bidsvalidator_installed():
    '''
    This function checks if the bids-validator command line tool is installed
    or not. If not, it installs it.
    Args:
        None
    Returns:
        None
    '''
    os.system('npm list -g bids-validator > tmp')
    temp = open('tmp', 'r').read()
    if 'empty' in temp:
        os.system('npm install -g bids-validator')
    os.system('rm tmp')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--output_dir", required=True,
                    help = "path to the BIDS output directory")
    args = vars(ap.parse_args())
    
    bids_json_path = './intermediate_files/bids.json'
    inter_file_path = './intermediate_files/intermediary.json'
    bids_folder = args["output_dir"]#'./bids_output'
    
    with open(bids_json_path, 'r') as file_loader:
        bids_json = json.load(file_loader)
        
    with open(inter_file_path, 'r') as file_loader:
        inter_file = json.load(file_loader)    
    
    generate_basic_files(bids_folder=bids_folder, data_description=inter_file['dataset_description'])

    bidsify_json(bids_folder, bids_json)
    
    ############# bids-validator ##############
    is_bidsvalidator_installed()
    os.system('bids-validator '+bids_folder+' > tmp')
    temp = open('tmp', 'r').read()
    print(temp)
    
    os.system('rm tmp')
    ###########################################
    

if __name__ == "__main__":
    main()