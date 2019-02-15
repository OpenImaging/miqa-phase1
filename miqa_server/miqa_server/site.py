from girder.api.rest import Resource
from girder.api import access
from girder.api.describe import Description, autoDescribeRoute
from girder.models.collection import Collection
from girder.models.folder import Folder
from girder.models.item import Item
from girder.exceptions import RestException


class Site(Resource):
    def __init__(self):
        super(Site, self).__init__()
        self.resourceName = 'miqa_site'

        self.route('GET', (), self.getAll)

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


def tryAddSites(sites, user):
    collection = Collection().findOne({'name': 'miqa'})
    sitesFolder = Folder().createFolder(
        collection, 'sites', parentType='collection',
        description='All sites configuration', reuseExisting=True)
    for site in sites:
        Item().createItem(site, user, sitesFolder, reuseExisting=True)


def getExtension(mime):
    if mime == 'image/jpeg':
        return '.jpg'
    elif mime == 'image/png':
        return '.png'
    return ''
