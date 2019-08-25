import os

from girder.api.rest import Resource
from girder.api import access
from girder.api.describe import Description, autoDescribeRoute
from girder.settings import SettingDefault
from girder.models.collection import Collection
from girder.models.folder import Folder
from girder.models.item import Item
from girder.models.setting import Setting
from girder.exceptions import RestException, ValidationException
from girder.utility import setting_utilities

from .constants import exportpathKey, importpathKey


class SettingResource(Resource):
    def __init__(self):
        super(SettingResource, self).__init__()
        self.resourceName = 'miqa_setting'

        self.route('GET', ('site',), self.getAll)
        self.route('GET', ('csvpath',), self.getCsvpath)
        self.route('POST', ('csvpath',), self.saveCsvpath)
        self.route('GET', ('import-export-enabled',), self.importExportEnabled)

    @access.user
    @autoDescribeRoute(
        Description('')
        .errorResponse())
    def getAll(self, params):
        collection = Collection().findOne({'name': 'miqa'})
        sitesFolder = Folder().createFolder(
            collection, 'sites', parentType='collection',
            description='All sites configuration', reuseExisting=True)
        return Folder().childItems(sitesFolder)

    @access.admin
    @autoDescribeRoute(
        Description('')
        .errorResponse())
    def getCsvpath(self, params):
        return self._getCsvpath()

    def _getCsvpath(self):
        importpath = Setting().get(importpathKey)
        exportpath = Setting().get(exportpathKey)
        return {
            'importpath': importpath if os.path.isfile(os.path.expanduser(importpath)) else '',
            'exportpath': exportpath if fileWritable(os.path.expanduser(exportpath)) else ''
        }

    @access.admin
    @autoDescribeRoute(
        Description('')
        .jsonParam('path', '', paramType='body', requireObject=True)
        .errorResponse())
    def saveCsvpath(self, path, params):
        Setting().set(importpathKey, path['importpath'])
        Setting().set(exportpathKey, path['exportpath'])

    @access.user
    @autoDescribeRoute(
        Description('')
        .errorResponse())
    def importExportEnabled(self, params):
        csvpath = self._getCsvpath()
        return {
            'import': bool(csvpath['importpath']),
            'export': bool(csvpath['exportpath'])
        }


def tryAddSites(sites, user):
    collection = Collection().findOne({'name': 'miqa'})
    sitesFolder = Folder().createFolder(
        collection, 'sites', parentType='collection',
        description='All sites configuration', reuseExisting=True)
    for site in sites:
        Item().createItem(site, user, sitesFolder, reuseExisting=True)


def fileWritable(path):
    if os.path.isfile(path):
        return os.access(path, os.W_OK)
    else:
        return os.access(os.sep.join(path.split(os.sep)[:-1]), os.W_OK)


def getExtension(mime):
    if mime == 'image/jpeg':
        return '.jpg'
    elif mime == 'image/png':
        return '.png'
    return ''


@setting_utilities.validator({
    importpathKey
})
def importpathValidate(doc):
    path = doc['value'].strip()
    if not os.path.isfile(os.path.expanduser(path)):
        raise ValidationException('%s must be a valid file path.' % doc['key'], 'value')
    doc['value'] = path


@setting_utilities.validator({
    exportpathKey
})
def exportpathValidate(doc):
    path = doc['value'].strip()
    if not fileWritable(os.path.expanduser(path)):
        raise ValidationException('%s needs to be a writable path.' % doc['key'], 'value')
    doc['value'] = path


SettingDefault.defaults.update({
    importpathKey: '',
    exportpathKey: ''
})
