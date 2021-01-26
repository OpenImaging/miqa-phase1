import datetime

from girder.api.rest import Resource
from girder.api import access
from girder.api.describe import Description, autoDescribeRoute
from girder import logger
from girder.models.collection import Collection
from girder.models.folder import Folder
from girder.models.item import Item
from girder.models.notification import Notification
from girder.models.file import File
from girder.models.user import User
from girder_jobs import Job
from girder_jobs.constants import JobStatus
from girder.exceptions import RestException, ValidationException
from miqa_worker_task.tasks import retrain_with_data_task
from miqa_worker_task.transform import TextToFile
from girder_worker_utils.transforms.girder_io import GirderUploadToItem, GirderClientTransform, GirderFileId

from .util import findSessionsFolder, findTempFolder, getExportCSV, importCSV


class Learning(Resource):
    def __init__(self):
        super(Learning, self).__init__()
        self.resourceName = 'learning'

        self.route('POST', ('retrain_with_data',), self.retrainWithData)

    @access.admin
    @autoDescribeRoute(
        Description('')
        .errorResponse())
    def retrainWithData(self, params):
        # learned from https://github.com/girder/large_image/blob/girder-3/girder/girder_large_image/models/image_item.py#L108
        user = self.getCurrentUser()
        item = Item().createItem('temp', user, findTempFolder(user, True))
        result = retrain_with_data_task.delay(
            TextToFile(getExportCSV()),
            girder_job_other_fields={'meta': {
                'creator': 'miqa',
                'itemId': str(item['_id']),
                'task': 'learning_with_data',
            }},
            girder_result_hooks=[
                GirderUploadToItem(str(item['_id']), delete_file=False),
            ]
        )
        return result.job

    @staticmethod
    def afterJobUpdate(job):
        # logger.info('^^^^^^^^^^ inside afterJobUpdate ^^^^^^^^^^')
        if job['status'] != JobStatus.SUCCESS:
            # logger.info('Sadly job status is {0} instead of SUCCESS'.format(job['status']))
            # logger.info(job)
            return
        meta = job.get('meta', {})
        item = Item().load(meta['itemId'], force=True)
        folder = Folder().load(item['folderId'], force=True)
        user = User().load(job.get('userId'), force=True)
        file = Item().childFiles(item)[0]
        csv_content = ''
        for chunk in File().download(file)():
            csv_content += chunk.decode("utf-8")
        # logger.info('Here is the json_content')
        # logger.info(csv_content)
        # For now just reimport instead of update, should update record instead
        result = importCSV(csv_content, user)
        Folder().remove(folder)
        # Throws an error for some reason, not really needed anyway
        # Job().updateJob(job, progressMessage="session re-evaluated")
        Notification().createNotification(
            type='miqa.learning_with_data',
            data=result,
            user={'_id': job.get('userId')},
            expires=datetime.datetime.utcnow() + datetime.timedelta(seconds=30))
