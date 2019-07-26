import csv
import datetime
import io
import os

from girder.api.rest import Resource, setResponseHeader, setContentDisposition
from girder.api import access, rest
from girder.constants import AccessType
from girder.exceptions import RestException
from girder.api.describe import Description, autoDescribeRoute
from girder.models.collection import Collection
from girder.models.folder import Folder
from girder.models.item import Item
from girder.models.setting import Setting
from girder.utility.progress import noProgress

from .setting import fileWritable, tryAddSites
from .constants import exportpathKey, importpathKey
from .util import findSessionsFolder, getExportCSV, importCSV


class Session(Resource):
    def __init__(self):
        super(Session, self).__init__()
        self.resourceName = 'miqa'

        self.route('POST', ('csv', 'import',), self.csvImport)
        self.route('GET', ('sessions',), self.getSessions)
        self.route('GET', ('csv', 'export',), self.csvExport)
        self.route('GET', ('csv', 'export', 'download',), self.csvExportDownload)

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
                datasets = list(Item().find({'$query': {'folderId': sessionFolder['_id'],
                                                        'name': {'$regex': 'nii.gz$'}}, '$orderby': {'name': 1}}))
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
    def csvImport(self, params):
        importpath = Setting().get(importpathKey)
        if not os.path.isfile(importpath):
            raise RestException('import csv file doesn\'t exists', code=404)
        with open(importpath) as csv_file:
            return importCSV(csv_file.read(), self.getCurrentUser())

    @access.user
    @autoDescribeRoute(
        Description('')
        .errorResponse())
    def csvExport(self, params):
        exportpath = Setting().get(exportpathKey)
        if not fileWritable(exportpath):
            raise RestException('export csv file is not writable', code=500)
        output = getExportCSV()
        with open(exportpath, 'w') as csv_file:
            csv_file.write(output.getvalue())

    @access.admin(cookie=True)
    @autoDescribeRoute(
        Description('')
        .errorResponse())
    def csvExportDownload(self, params):
        setResponseHeader('Content-Type', 'text/csv')
        setContentDisposition('_output.csv')
        output = getExportCSV()
        return lambda: [(yield x) for x in output.getvalue()]
