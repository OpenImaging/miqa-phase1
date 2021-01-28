import os

from girder import logger
from girder_worker.app import app
from girder_worker.utils import girder_job


@girder_job(title='Retrain with data')
@app.task(bind=True)
def retrain_with_data_task(self, csv_file_path, learningMode):
    # the path where the master_folder exists
    master_path = os.environ['MIQA_MRIQC_PATH']

    if learningMode == 'neuralNetwork':
        return neuralNetworkTrain(master_path, csv_file_path)
    else:
        return randomForestTrain(master_path, csv_file_path)


def neuralNetworkTrain(master_path, csv_file_path):
    from mriqc.active_learner import train

    logger.info('Performing neuralNetworkTrain({0}, {1})'.format(master_path, csv_file_path))
    return train(master_path, csv_file_path)


def randomForestTrain(master_path, csv_file_path):
    from mriqc.active_learner import train

    logger.info('Performing randomForestTrain({0}, {1})'.format(master_path, csv_file_path))
    return train(master_path, csv_file_path)