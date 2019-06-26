# Including MRIQC to MIQA

### Brief overview

MRIQC is an opensource tool that generates Image Quality Metrics(IQMs) for the NIFTI images. But it requires the dataset to be in Brain Imaging Data Structure(BIDS) format. Since, the dataset being yielded by the MIQA tool is in a custom format, thus, we need to have our own scripts that convert our dataset to the BIDS format. Then, these can be processed using the docker container of the MRIQC to generate the IQMs for each image.

### Requirements

To exrtact, one needs to fulfill the following requirements:

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
python data2mriqc.py -ci '/home/dhruv.sharma/Projects/MRIQC_AL/miqa sample data/sample data new/scans_to_review-2019-01-23.csv' 
                     -r '/home/dhruv.sharma/Projects/MRIQC_AL/miqa sample data/sample data new/datasnap-2019-01-23' 
                     -bo '/home/dhruv.sharma/Projects/MRIQC_AL/data2bids/bids_output/' 
                     -mo "/home/dhruv.sharma/Projects/MRIQC_AL/data2bids/mriqc_output/" 
                     -co "/home/dhruv.sharma/Projects/MRIQC_AL/mriqc_output.csv"
```
