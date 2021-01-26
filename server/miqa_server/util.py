import datetime
import json
from jsonschema import validate
from jsonschema.exceptions import ValidationError as JSONValidationError
import os

from girder.exceptions import RestException
from girder import logger
from girder.models.assetstore import Assetstore
from girder.models.collection import Collection
from girder.models.folder import Folder
from girder.models.item import Item
from girder.utility.progress import noProgress

from .conversion.csv_to_json import csvContentToJsonObject
from .conversion.json_to_csv import jsonObjectToCsvContent
from .setting import tryAddSites
from .schema.data_import import schema


def parseIQM(iqm):
    if not iqm:
        return None
    rows = iqm.split(';')
    metrics = []
    for row in rows:
        if not row:
            continue
        [key, value] = row.split(':')
        value = float(value)
        elements = key.split('_')
        if len(elements) == 1:
            metrics.append({key: value})
        else:
            type_ = '_'.join(elements[:-1])
            subType = elements[-1]
            if(list(metrics[-1].keys())[0]) != type_:
                metrics.append({type_: []})
            subTypes = metrics[-1][type_]
            subTypes.append({subType: value})
    return metrics


def findFolder(name, user=None, create=False):
    collection = Collection().findOne({'name': 'miqa'})
    folder = Folder().findOne({'name': name, 'baseParentId': collection['_id']})
    if not create:
        return folder
    elif not folder:
        return Folder().createFolder(collection, name,
                                     parentType='collection', creator=user)
    else:
        return folder


def findSessionsFolder(user=None, create=False):
    return findFolder('sessions', user, create)


def findTempFolder(user=None, create=False):
    return findFolder('temp', user, create)


def tryGetExistingSessionMeta(sessionsFolder, experimentId, scan):
    experimentFolder = Folder().findOne(
        {'name': experimentId, 'parentId': sessionsFolder['_id']})
    if not experimentFolder:
        return None
    sessionFolder = Folder().findOne(
        {'name': scan, 'parentId': experimentFolder['_id']})
    if not sessionFolder:
        return None
    return sessionFolder.get('meta', {})


def importJson(json_content, user):
    existingSessionsFolder = findSessionsFolder(user)
    if existingSessionsFolder:
        existingSessionsFolder['name'] = 'sessions_' + \
            datetime.datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
        Folder().save(existingSessionsFolder)
    sessionsFolder = findSessionsFolder(user, True)
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
        # Merge note and rating if record exists
        if existingSessionsFolder:
            existingMeta = tryGetExistingSessionMeta(
                existingSessionsFolder, experimentId, scanName)
            if(existingMeta and (existingMeta.get('note', None) or existingMeta.get('rating', None))):
                meta['note'] = existingMeta.get('note', None)
                meta['rating'] = existingMeta.get('rating', None)
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
        itemMeta = {}
        iqm = parseIQM(scan['iqms'])
        if iqm:
            itemMeta['iqm'] = iqm
        good_prob = None
        try:
            good_prob = float(scan['good_prob'])
        except:
            pass
        if good_prob:
            itemMeta['goodProb'] = good_prob
        if itemMeta:
            item = list(Folder().childItems(scanFolder, limit=1))[0]
            Item().setMetadata(item, itemMeta, allowNull=True)
        successCount += 1

    tryAddSites(sites, user)

    return {
        "success": successCount,
        "failed": failedCount
    }


def importCSV(csv_content, user):
    try:
        json_content = csvContentToJsonObject(csv_content)
        validate(json_content, schema)
    except (JSONValidationError, Exception) as inst:
        return {
            "error": 'Invalid CSV file: {0}'.format(inst.message),
        }

    return importJson(json_content, user)


def importData(importpath, user):
    json_content = None

    if importpath.endswith('.csv'):
        with open(importpath) as fd:
            return importCSV(fd.read(), user)
    else:
        with open(importpath) as json_file:
            json_content = json.load(json_file)

            try:
                validate(json_content, schema)
            except JSONValidationError as inst:
                return {
                    "error": 'Invalid JSON file: {0}'.format(inst.message),
                }

            return importJson(json_content, user)


def getExportJSONObject():
    def convertRatingToDecision(rating):
        return {
            None: 0,
            'questionable': 0,
            'good': 1,
            'usableExtra': 2,
            'bad': -1
        }[rating]
    sessionsFolder = findSessionsFolder()
    items = list(Folder().childItems(sessionsFolder, filters={'name': 'json'}))
    if not len(items):
        raise RestException('doesn\'t contain a json item', code=404)
    jsonItem = items[0]
    # Next TODO: read, format, and stream back the json version of the export
    # logger.info(jsonItem)
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


def getExportJSON():
    return json.dumps(getExportJSONObject())


def getExportCSV():
    return jsonObjectToCsvContent(getExportJSONObject())
