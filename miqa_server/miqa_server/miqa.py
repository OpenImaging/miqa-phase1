from girder.api.rest import Resource
from girder.api import access, rest
from girder.exceptions import RestException
from girder.api.describe import Description, autoDescribeRoute
from girder.models.collection import Collection
from girder.models.folder import Folder
from girder.models.item import Item


class Miqa(Resource):
    def __init__(self):
        super(Miqa, self).__init__()
        self.resourceName = 'miqa'

        self.route('GET', ('sessions',), self.getAllSessions)

    @access.public
    @autoDescribeRoute(
        Description('Retrieve all sessions in a tree structure')
        .errorResponse())
    def getAllSessions(self, params):
        user = self.getCurrentUser()
        result = []
        collection = Collection().findOne({'name': 'miqa'})
        for batchFolder in Folder().childFolders(collection, 'collection', user=user):
            sessions = []
            result.append({
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
        return result
