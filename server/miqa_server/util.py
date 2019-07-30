import csv
import datetime
import io
import os

from girder.exceptions import RestException
from girder.models.collection import Collection
from girder.models.folder import Folder
from girder.models.item import Item
from girder.models.assetstore import Assetstore
from girder.utility.progress import noProgress

from .setting import tryAddSites


def findSessionsFolder(user=None, create=False):
    return findFolder('sessions', user, create)


def findTempFolder(user=None, create=False):
    return findFolder('temp', user, create)


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


def importCSV(csv_content, user):
    existingSessionsFolder = findSessionsFolder(user)
    if existingSessionsFolder:
        existingSessionsFolder['name'] = 'sessions_' + \
            datetime.datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
        Folder().save(existingSessionsFolder)
    sessionsFolder = findSessionsFolder(user, True)
    Item().createItem('csv', user, sessionsFolder, description=csv_content)
    reader = csv.DictReader(io.StringIO(csv_content))
    successCount = 0
    failedCount = 0
    sites = set()
    for row in reader:
        experimentId = row['xnat_experiment_id']
        niftiPath = row['nifti_folder']
        experimentNote = row['experiment_note']
        splits = niftiPath.split('/')
        site = splits[5].split('_')[0]
        sites.add(site)
        experimentId2 = '-'.join(splits[7].split('-')[0:-1])
        date = splits[7].split('-')[-1]
        scanId = row['scan_id']
        scanType = row['scan_type']
        scan = scanId+'_'+scanType
        niftiFolder = os.path.join(niftiPath, scan)
        if not os.path.isdir(niftiFolder):
            failedCount += 1
            continue
        experimentFolder = Folder().createFolder(
            sessionsFolder, experimentId, parentType='folder', reuseExisting=True)
        scanFolder = Folder().createFolder(
            experimentFolder, scan, parentType='folder', reuseExisting=True)
        meta = {
            'experimentId': experimentId,
            'experimentId2': experimentId2,
            'experimentNote': experimentNote,
            'site': site,
            'date': date,
            'scanId': scanId,
            'scanType': scanType
        }
        # Merge note and rating if record exists
        if existingSessionsFolder:
            existingMeta = tryGetExistingSessionMeta(
                existingSessionsFolder, experimentId, scan)
            if(existingMeta and (existingMeta.get('note', None) or existingMeta.get('rating', None))):
                meta['note'] = existingMeta.get('note', None)
                meta['rating'] = existingMeta.get('rating', None)
        Folder().setMetadata(scanFolder, meta)
        currentAssetstore = Assetstore().getCurrent()
        Assetstore().importData(
            currentAssetstore, parent=scanFolder, parentType='folder', params={
                'fileIncludeRegex': '.+[.]nii[.]gz$',
                'importPath': niftiFolder,
            }, progress=noProgress, user=user, leafFoldersAsItems=False)
        itemMeta = {}
        iqm = parseIQM(row['IQMs'])
        if iqm:
            itemMeta['iqm'] = iqm
        good_prob = None
        try:
            good_prob = float(row['good_prob'])
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


def getExportCSV():
    def convertRatingToDecision(rating):
        return {
            None: 0,
            'questionable': 0,
            'good': 1,
            'usableExtra': 2,
            'bad': -1
        }[rating]
    sessionsFolder = findSessionsFolder()
    items = list(Folder().childItems(sessionsFolder, filters={'name': 'csv'}))
    if not len(items):
        raise RestException('doesn\'t contain a csv item', code=404)
    csvItem = items[0]
    reader = csv.DictReader(io.StringIO(csvItem['description']))
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=reader.fieldnames)
    writer.writeheader()
    for row in reader:
        experience = Folder().findOne({
            'name': row['xnat_experiment_id'],
            'parentId': sessionsFolder['_id']
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
    return output
