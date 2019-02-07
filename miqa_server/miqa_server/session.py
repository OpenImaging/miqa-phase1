import csv
import time
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
from girder.models.assetstore import Assetstore
from girder.utility.progress import noProgress


class Session(Resource):
    def __init__(self):
        super(Session, self).__init__()
        self.resourceName = 'miqa'

        self.route('POST', ('batch', 'csv',), self.csvImport)
        self.route('GET', ('batch',), self.getAllbatch)
        self.route('GET', ('batch', ':id', 'sessions',), self.getBatchSessions)
        self.route('GET', ('batch', ':id', 'export',), self.getBatchCsvResult)
        self.route('GET', ('dataset', ':id', 'sessions',), self.getDatasetSessions)

    @access.user
    @autoDescribeRoute(
        Description('Retrieve all batches')
        .errorResponse())
    def getAllbatch(self, params):
        user = self.getCurrentUser()
        result = []
        collection = Collection().findOne({'name': 'miqa'})
        if not collection:
            return result
        return [{'name': folder['name'], '_id':folder['_id']} for folder in Folder().childFolders(collection, 'collection', user=user)]

    @access.user
    @autoDescribeRoute(
        Description('Retrieve all sessions of a batch in a tree structure')
        .modelParam('id', model=Folder, level=AccessType.READ, destName='batch')
        .errorResponse())
    def getBatchSessions(self, batch, params):
        return self.getSessions(batch)

    @access.user
    @autoDescribeRoute(
        Description('Retrieve all sessions of a batch in a tree structure')
        .modelParam('id', model=Item, level=AccessType.READ, destName='dataset')
        .errorResponse())
    def getDatasetSessions(self, dataset, params):
        user = self.getCurrentUser()
        batch = Item().parentsToRoot(dataset, user=user)[1]['object']
        return self.getSessions(batch)

    def getSessions(self, batch):
        user = self.getCurrentUser()
        experiments = []
        for batchFolder in Folder().childFolders(batch, 'folder', user=user):
            sessions = []
            experiments.append({
                'folderId': batchFolder['_id'],
                'name': batchFolder['name'],
                'sessions': sessions
            })
            for sessionFolder in Folder().childFolders(batchFolder, 'folder', user=user):
                datasets = list(Item().find({'folderId': sessionFolder['_id'],
                                             'name': {'$regex': 'nii.gz$'}}))
                sessions.append({
                    'folderId': sessionFolder['_id'],
                    'name': sessionFolder['name'],
                    'datasets': datasets
                })
        return {
            'batch': {
                '_id': batch['_id'],
                'name': batch['name']
            },
            'experiments': experiments
        }

    @access.admin
    @autoDescribeRoute(
        Description('')
        .param('filename', '', required=True, dataType='string', paramType='query')
        .param('body', '', required=True, dataType='string', paramType='body')
        .errorResponse())
    def csvImport(self, filename, body, params):
        user = self.getCurrentUser()
        csv_content = body.read().decode("utf-8")
        collection = Collection().findOne({'name': 'miqa'})
        batchFolder = Folder().createFolder(collection, filename,
                                            parentType='collection', creator=user, allowRename=True)
        Item().createItem('csv', user, batchFolder, description=csv_content)
        reader = csv.DictReader(io.StringIO(csv_content))
        successCount = 0
        failedCount = 0
        for row in reader:
            scan = row['scan_id']+'_'+row['scan_type']
            if not os.path.isdir(row['nifti_folder']+'/'+scan):
                failedCount += 1
                continue
            experimentFolder = Folder().createFolder(
                batchFolder, row['xnat_experiment_id'], parentType='folder', reuseExisting=True)
            scanFolder = Folder().createFolder(
                experimentFolder, scan, parentType='folder', reuseExisting=True)

            currentAssetstore = Assetstore().getCurrent()
            Assetstore().importData(
                currentAssetstore, parent=scanFolder, parentType='folder', params={
                    'importPath': row['nifti_folder']+'/'+scan,
                }, progress=noProgress, user=user, leafFoldersAsItems=False)
            successCount += 1
        return {
            "success": successCount,
            "failed": failedCount
        }

    @access.user
    @access.cookie
    @autoDescribeRoute(
        Description('')
        .modelParam('id', model=Folder, level=AccessType.READ, destName='batch')
        .errorResponse())
    def getBatchCsvResult(self, batch, params):
        def convertRatingToDecision(rating):
            return {
                None: 0,
                'good': 1,
                'usableExtra': 2,
                'bad': -1
            }[rating]
        setResponseHeader('Content-Type', 'text/csv')
        setContentDisposition(batch['name'] + '_output.csv')
        items = list(Folder().childItems(batch, filters={'name': 'csv'}))
        if not len(items):
            raise RestException('Batch doesn\'t contain a csv item', code=404)
        csvItem = items[0]
        reader = csv.DictReader(io.StringIO(csvItem['description']))
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=reader.fieldnames)
        for row in reader:
            experience = Folder().findOne({
                'name': row['xnat_experiment_id'],
                'parentId': batch['_id']
            })
            if not experience:
                continue
            session = Folder().findOne({
                'name': row['scan_id']+'_'+row['scan_type'],
                'parentId': experience['_id']
            })
            if not session:
                continue
            row['decision'] = convertRatingToDecision(session.get('meta', {}).get('rating', None))
            row['scan_note'] = session.get('meta', {}).get('note', None)
            writer.writerow(row)
        return lambda: [(yield x) for x in output.getvalue()]
