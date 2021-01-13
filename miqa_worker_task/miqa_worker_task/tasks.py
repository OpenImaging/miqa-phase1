import os

from girder_worker.app import app
from girder_worker.utils import girder_job


@girder_job(title='Retrain with data')
@app.task(bind=True)
def retrain_with_data_task(self, csv_file_path):
    from mriqc.active_learner import train

    # the path where the master_folder exists
    master_path = os.environ['MIQA_MRIQC_PATH']

    return train(master_path, csv_file_path)