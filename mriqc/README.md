# Including MRIQC to MIQA

### Brief overview

MRIQC is an opensource tool that generates Image Quality Metrics(IQMs) for the NIFTI images. But it requires the dataset to be in Brain Imaging Data Structure(BIDS) format. Since, the dataset being yielded by the MIQA tool is in a custom format, thus, we need to have our own scripts that convert our dataset to the BIDS format. Then, these can be processed using the docker container of the MRIQC to generate the IQMs for each image.

### Requirements

To extract, one needs to fulfill the following requirements:

* Python 3.5 or above
* NPM
* docker

### Generating the MRIQC csv

The `data2mriqc.py` is the engine file that runs all the processes to generate the csv file containing IQMs for each subject. You can do `python data2mriqc.py --help` to get to know the input requirements.

Inputs(paths should be absolute paths):

1. path to the input csv
2. root path to the folder where images start
3. path to the BIDS output 
4. path to the MRIQC output
5. path to the csv containing the MRIQC metrics for each subject

For example:
```
python data2mriqc.py -ci "/home/dhruv.sharma/Projects/MRIQC_AL/miqa sample data/sample data new/scans_to_review-2019-01-23.csv" \
                     -r "/home/dhruv.sharma/Projects/MRIQC_AL/miqa sample data/sample data new/datasnap-2019-01-23" \
                     -bo "/home/dhruv.sharma/Projects/MRIQC_AL/data2bids/bids_output/" \
                     -mo "/home/dhruv.sharma/Projects/MRIQC_AL/data2bids/mriqc_output/" \
                     -co "/home/dhruv.sharma/Projects/MRIQC_AL/mriqc_output.csv"
```

# Active Learning and MIQA

### Brief Overview

This module is to plug-in the active learning framework with the web-based application of MIQA. The module takes in the user input in CSV format and makes predictions on the quality of the image. These predictions are then displayed to the user on the MIQA platform for their feedback. The decision of the user is then taken into account to retrain the model and update the weights by selecting only the most informative data points. The most informative points are selected using the query strategies of the active learning framework.

### Requirements

The requirements have been defined in `requirements.txt` and can be installed using `pip install -r requirements.txt`. Also, place the master folder the appropriate location. The structure of the master folder should be as follows:
```
master_folder/
├── data_with_labels
│   ├── data_1.csv
│   └── data_2.csv
├── data_with_preds
│   ├── data_1.csv
│   └── data_2.csv
├── model_weights
└── training_data.csv
 
```

### Using the module 

The `active_learner.py` has two functions:
* predict() : This function takes the two inputs - path to master_folder, and path to the input csv. It returns the path to the new csv with an added column `good_prob` which contains the prediction scores for the image quality.
Function signature is as follows:
```
Args:
    master_path: the absolute path to the master folder with all important directories like training_data.csv, model_weights, log files
    path: path to the csv file with the new input data
Returns:
    path: the new path to the file with the new input data
```

* train() : This function also takes two inputs - path to master_folder, and path to the input csv(optional). If path to input csv is not provided, it trains on the already available data and saves the model. If the path is provided, it picks the most informative labeled data points and adds them to the training data. Then, the model is retrained on this new data and the input CSV is updated with the new prediction scores.
Function signature is as follows:
```
Args:
    master_path: the absolute path to the master folder with all important directories like training_data.csv, model_weights, log files
    csv_path: the path to the csv containing the newly labeled data
Returns:
    None
```
