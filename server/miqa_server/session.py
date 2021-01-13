import datetime
import io
import json
import os

from girder.api.rest import Resource, setResponseHeader, setContentDisposition
from girder.api import access, rest
from girder.constants import AccessType
from girder.exceptions import RestException
from girder.api.describe import Description, autoDescribeRoute
from girder.models.folder import Folder
from girder.models.item import Item
from girder.models.setting import Setting
from girder.utility.progress import noProgress

from .setting import fileWritable
from .constants import exportpathKey, importpathKey
from .util import findSessionsFolder, getExportJSON, importData


class Session(Resource):
    def __init__(self):
        super(Session, self).__init__()
        self.resourceName = 'miqa'

        self.route('POST', ('data', 'import',), self.dataImport)
        self.route('GET', ('sessions',), self.getSessions)
        self.route('GET', ('data', 'export',), self.dataExport)

    @access.user
    @autoDescribeRoute(
        Description('Retrieve all sessions in a tree structure')
        .errorResponse())
    def getSessions(self, params):
        return self._getSessions()

    def _getSessions(self):
        user = self.getCurrentUser()
        sessionsFolder = findSessionsFolder()
        if not sessionsFolder:
            return []
        experiments = []
        for experimentFolder in Folder().childFolders(sessionsFolder, 'folder', user=user):
            sessions = []
            experiments.append({
                'folderId': experimentFolder['_id'],
                'name': experimentFolder['name'],
                'sessions': sessions
            })
            for sessionFolder in Folder().childFolders(experimentFolder, 'folder', user=user):
                orderItem = Item().findOne({'name': 'imageOrderDescription',
                                            'folderId': sessionFolder['_id']})
                descriptionJson = json.loads(orderItem['description'])
                orderDescription = descriptionJson['orderDescription']
                if 'images' in orderDescription:
                    imageOrderList = orderDescription['images']
                    unordered_data = list(Item().find({
                        '$query': {
                            'folderId': sessionFolder['_id'],
                        }
                    }))
                    datasets = [None] * (len(unordered_data) - 1)
                    for dataset in unordered_data:
                        if dataset['name'] != 'imageOrderDescription':
                            insertIndex = imageOrderList.index(dataset['name'])
                            datasets[insertIndex] = dataset
                elif 'imagePattern' in orderDescription:
                    imagePattern = orderDescription['imagePattern']
                    datasets = list(Item().find({
                        '$query': {
                            'folderId': sessionFolder['_id'],
                            'name': {
                                '$regex': 'nii.gz$'
                            }
                        },
                        '$orderby': {
                            'name': 1
                        }
                    }))
                else:
                    raise RestException('Scan folder does not contain expected image ordering information')

                sessions.append({
                    'folderId': sessionFolder['_id'],
                    'name': sessionFolder['name'],
                    'meta': sessionFolder.get('meta', {}),
                    'datasets': datasets
                })
        return experiments

    @access.user
    @autoDescribeRoute(
        Description('')
        .errorResponse())
    def dataImport(self, params):
        importpath = os.path.expanduser(Setting().get(importpathKey))
        if not os.path.isfile(importpath):
            raise RestException('import path does not exist ({0}'.format(importpath), code=404)

        return importData(importpath, self.getCurrentUser())


    @access.user
    @autoDescribeRoute(
        Description('')
        .errorResponse())
    def dataExport(self, params):
        exportpath = os.path.expanduser(Setting().get(exportpathKey))
        if not fileWritable(exportpath):
            raise RestException('export json file is not writable', code=500)
        output = getExportJSON()
        with open(exportpath, 'w') as json_file:
            json_file.write(output)
