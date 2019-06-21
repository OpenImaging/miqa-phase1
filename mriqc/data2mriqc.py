#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 16:39:21 2019

@author: dhruv.sharma
"""

from process_iqms import get_iqms, generate_csv
from data2bids.restructure_files import get_csv_contents, get_initial_dict, add_subject_data, group_by_subject
from data2bids.generate_bids_json import populate_bids_json
from data2bids.bidsify import generate_basic_files, bidsify_json, is_bidsvalidator_installed
import os
import argparse

'''
python data2mriqc.py -ci '/home/dhruv.sharma/Projects/MRIQC_AL/miqa sample data/sample data new/scans_to_review-2019-01-23.csv' 
                     -r '/home/dhruv.sharma/Projects/MRIQC_AL/miqa sample data/sample data new/datasnap-2019-01-23' 
                     -bo '../../data2bids/bids_output/' 
                     -mo "../../data2bids/mriqc_output/" 
                     -co "../../mriqc_output.csv"
'''

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-ci", "--csv_input_path", required=True,
                    help = "path to the csv file")
    ap.add_argument("-r", "--root", required=True,
                    help = "absolute path to the image root folder")
    ap.add_argument("-bo", "--bids_output_dir", required=True,
                    help = "path to the BIDS output directory")
    ap.add_argument("-mo", "--mriqc_output_path", required=True,
                    help = "path to the MRIQC output directory")
    ap.add_argument("-co", "--csv_output_path", required=True,
                    help = "path to save the processed csv file")
    
    args = vars(ap.parse_args())
    
    csv_input_path = args["csv_input_path"]#'/home/dhruv.sharma/Projects/MRIQC_AL/miqa sample data/sample data new/scans_to_review-2019-01-23.csv'
    root_path = args["root"]#'/home/dhruv.sharma/Projects/MRIQC_AL/miqa sample data/sample data new/datasnap-2019-01-23'
    bids_output_path = args["bids_output_dir"]# '../../data2bids/bids_output/'
    mriqc_output = args["mriqc_output_path"]#"../../data2bids/mriqc_output/"
    csv_output_path = args["csv_output_path"]# "../../mriqc_output.csv"
    
    csv_content = get_csv_contents(csv_input_path)
    subject_wise_data = group_by_subject(csv_content)
#    print(subject_wise_data['E08706'])
    
    inter_file = get_initial_dict()
    add_subject_data(data_dict=inter_file, 
                     all_subject_data=subject_wise_data,
                     root_path=root_path)
    
    bids_json = populate_bids_json(inter_file['data'])
    
    generate_basic_files(bids_folder=bids_output_path, data_description=inter_file['dataset_description'])
    bidsify_json(bids_output_path, bids_json)
    
    is_bidsvalidator_installed()
    os.system('bids-validator '+bids_output_path+' > tmp')
    temp = open('tmp', 'r').read()
    print(temp)
    
    os.system('rm tmp')
    
    ############
    #MRIQC command
    # input -> bids_output_path, mriqc_output_path
    '''
    command = 'docker run -ti --rm -v '+bids_output_path+':/bids_dataset:ro -v '+mriqc_output+':/output poldracklab/mriqc:latest /bids_dataset /output participant --participant_label'
    os.system(command)
    '''
    ############
    
    iqms, iqm_values = get_iqms(mriqc_output)
    generate_csv(csv_output_path, iqms, iqm_values)
    
if __name__ == '__main__':
    main()
    
    