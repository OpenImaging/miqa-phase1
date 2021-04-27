import datetime
import io
import json
from jsonschema import validate
from jsonschema.exceptions import ValidationError as JSONValidationError
import os

from girder.api.rest import Resource, setResponseHeader, setContentDisposition
from girder.api import access, rest
from girder.constants import AccessType
from girder.exceptions import RestException
from girder.api.describe import Description, autoDescribeRoute
from girder import logger
from girder.models.collection import Collection
from girder.models.assetstore import Assetstore
from girder.models.folder import Folder
from girder.models.item import Item
from girder.models.setting import Setting
from girder.utility.progress import noProgress

from .conversion.csv_to_json import csvContentToJsonObject
from .conversion.json_to_csv import jsonObjectToCsvContent
from .setting import fileWritable, tryAddSites
from .constants import exportpathKey, importpathKey
from .schema.data_import import schema


def convertRatingToDecision(rating):
    return {
        None: '',
        '': '',
        'bad': 0,
        'good': 1,
        'usableExtra': 2
    }[rating]


def convertDecisionToRating(decision):
    if decision == None or decision == '':
        return ''
    num_decision = int(decision)
    if num_decision == 0:
        return 'bad'
    elif num_decision == 1:
        return 'good'
    elif num_decision == 2:
        return 'usableExtra'
    return 'unknown'


class Session(Resource):
    def __init__(self):
        super(Session, self).__init__()
        self.resourceName = 'miqa'

        self.route('POST', ('data', 'import',), self.dataImport)
        self.route('GET', ('sessions',), self.getSessions)
        self.route('GET', ('data', 'export',), self.dataExport)
        self.route('GET', ('sessiontime',), self.getRemainingSessionTime)

    @access.user
    @autoDescribeRoute(
        Description('Return number of seconds until token expires')
        .errorResponse())
    def getRemainingSessionTime(self, params):
        curToken = self.getCurrentToken()
        currentTime = datetime.datetime.utcnow()
        tokenExpireTime = curToken['expires']
        remainingSessionTime = tokenExpireTime - currentTime
        return remainingSessionTime.total_seconds()

    @access.user
    @autoDescribeRoute(
        Description('Retrieve all sessions in a tree structure')
        .errorResponse())
    def getSessions(self, params):
        return self._getSessions()

    def _getSessions(self):
        user = self.getCurrentUser()
        sessionsFolder = self.findSessionsFolder()
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
        user = self.getCurrentUser()
        importpath = os.path.expanduser(Setting().get(importpathKey))
        if not os.path.isfile(importpath):
            raise RestException('import path does not exist ({0}'.format(importpath), code=404)

        json_content = None

        if importpath.endswith('.csv'):
            with open(importpath) as fd:
                csv_content = fd.read()
                try:
                    json_content = csvContentToJsonObject(csv_content)
                    validate(json_content, schema)
                except (JSONValidationError, Exception) as inst:
                    return {"error": 'Invalid CSV file: {0}'.format(inst.message)}
        else:
            with open(importpath) as json_file:
                json_content = json.load(json_file)
                try:
                    validate(json_content, schema)
                except JSONValidationError as inst:
                    return {"error": 'Invalid JSON file: {0}'.format(inst.message)}

        existingSessionsFolder = self.findSessionsFolder(user)
        if existingSessionsFolder:
            existingSessionsFolder['name'] = 'sessions_' + \
                datetime.datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
            Folder().save(existingSessionsFolder)
        sessionsFolder = self.findSessionsFolder(user, True)
        Item().createItem('json', user, sessionsFolder, description=json.dumps(json_content))

        datasetRoot = json_content['data_root']
        experiments = json_content['experiments']
        sites = json_content['sites']

        successCount = 0
        failedCount = 0
        sites = set()
        for scan in json_content['scans']:
            experimentId = scan['experiment_id']
            experimentNote = ''
            for experiment in experiments:
                if experiment['id'] == experimentId:
                    experimentNote = experiment['note']
            scanPath = scan['path']
            site = scan['site_id']
            sites.add(site)
            scanId = scan['id']
            scanType = scan['type']
            scanName = scanId+'_'+scanType
            niftiFolder = os.path.expanduser(os.path.join(datasetRoot, scanPath))
            if not os.path.isdir(niftiFolder):
                failedCount += 1
                continue
            experimentFolder = Folder().createFolder(
                sessionsFolder, experimentId, parentType='folder', reuseExisting=True)
            scanFolder = Folder().createFolder(
                experimentFolder, scanName, parentType='folder', reuseExisting=True)
            meta = {
                'experimentId': experimentId,
                'experimentNote': experimentNote,
                'site': site,
                'scanId': scanId,
                'scanType': scanType
            }
            if 'decision' in scan:
                meta['rating'] = convertDecisionToRating(scan['decision'])
            if 'note' in scan:
                meta['note'] = scan['note']
            Folder().setMetadata(scanFolder, meta)
            currentAssetstore = Assetstore().getCurrent()
            if 'images' in scan:
                scanImages = scan['images']
                # Import images one at a time because the user provided a list
                for scanImage in scanImages:
                    absImagePath = os.path.join(niftiFolder, scanImage)
                    Assetstore().importData(
                        currentAssetstore, parent=scanFolder, parentType='folder', params={
                            'fileIncludeRegex': '^{0}$'.format(scanImage),
                            'importPath': niftiFolder,
                        }, progress=noProgress, user=user, leafFoldersAsItems=False)
                imageOrderDescription = {
                    'orderDescription': {
                        'images': scanImages
                    }
                }
            else:
                scanImagePattern = scan['imagePattern']
                # Import all images in directory at once because user provide a file pattern
                Assetstore().importData(
                    currentAssetstore, parent=scanFolder, parentType='folder', params={
                        'fileIncludeRegex': scanImagePattern,
                        'importPath': niftiFolder,
                    }, progress=noProgress, user=user, leafFoldersAsItems=False)
                imageOrderDescription = {
                    'orderDescription': {
                        'imagePattern': scanImagePattern
                    }
                }
            Item().createItem(name='imageOrderDescription',
                              creator=user,
                              folder=scanFolder,
                              reuseExisting=True,
                              description=json.dumps(imageOrderDescription))
            successCount += 1
        tryAddSites(sites, self.getCurrentUser())
        return {
            "success": successCount,
            "failed": failedCount
        }

    @access.user
    @autoDescribeRoute(
        Description('')
        .errorResponse())
    def dataExport(self, params):
        exportpath = os.path.expanduser(Setting().get(exportpathKey))
        if not fileWritable(exportpath):
            raise RestException('export file path is not writable', code=500)

        output = None

        if exportpath.endswith('.csv'):
            csvStringIO = self.getExportCSV()
            output = csvStringIO.getvalue()
        else:
            output = self.getExportJSON()

        with open(exportpath, 'w') as fd:
            fd.write(output)

    def getExportJSONObject(self):
        sessionsFolder = self.findSessionsFolder()
        items = list(Folder().childItems(sessionsFolder, filters={'name': 'json'}))
        if not len(items):
            raise RestException('doesn\'t contain a json item', code=404)
        jsonItem = items[0]
        # Next TODO: read, format, and stream back the json version of the export
        original_json_object = json.loads(jsonItem['description'])

        for scan in original_json_object['scans']:
            experiment = Folder().findOne({
                'name': scan['experiment_id'],
                'parentId': sessionsFolder['_id']
            })
            if not experiment:
                continue
            session = Folder().findOne({
                'name': '{0}_{1}'.format(scan['id'], scan['type']),
                'parentId': experiment['_id']
            })
            if not session:
                continue
            scan['decision'] = convertRatingToDecision(session.get('meta', {}).get('rating', None))
            scan['note'] = session.get('meta', {}).get('note', None)

        return original_json_object

    def getExportJSON(self):
        return json.dumps(self.getExportJSONObject())

    def getExportCSV(self):
        return jsonObjectToCsvContent(self.getExportJSONObject())

    def findSessionsFolder(self, user=None, create=False):
        collection = Collection().findOne({'name': 'miqa'})
        sessionsFolder = Folder().findOne({'name': 'sessions', 'baseParentId': collection['_id']})
        if not create:
            return sessionsFolder
        else:
            if not sessionsFolder:
                return Folder().createFolder(collection, 'sessions',
                                             parentType='collection', creator=user)

    def tryGetExistingSessionMeta(self, sessionsFolder, experimentId, scan):
        experimentFolder = Folder().findOne(
            {'name': experimentId, 'parentId': sessionsFolder['_id']})
        if not experimentFolder:
            return None
        sessionFolder = Folder().findOne(
            {'name': scan, 'parentId': experimentFolder['_id']})
        if not sessionFolder:
            return None
        return sessionFolder.get('meta', {})
