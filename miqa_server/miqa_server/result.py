import csv
import io

from girder import events
from girder.api.rest import Resource, setResponseHeader, setContentDisposition
from girder.api import access
from girder.api.describe import Description, autoDescribeRoute
from girder.constants import AccessType
from girder.exceptions import RestException
from girder.models.folder import Folder


class Result(Resource):
    def __init__(self):
        super(Result, self).__init__()
        self.resourceName = 'result'

        self.route('GET', (':id',), self.getResult)

    @access.user
    @access.cookie
    @autoDescribeRoute(
        Description('')
        .modelParam('id', '', model=Folder, level=AccessType.READ)
        .errorResponse())
    def getResult(self, folder, params):
        setResponseHeader('Content-Type', 'text/csv')
        setContentDisposition(folder['name'] + '.csv')
        user = self.getCurrentUser()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['scan_type', 'experiment_note', 'decision', 'reviewer'])
        for folder in Folder().childFolders(folder, 'folder', user=user):
            values = [folder['name']]
            meta = folder.get('meta', None)
            if meta:
                values += [meta['note'], meta['rating'], meta['reviewer']]
            writer.writerow(values)
        return lambda: [(yield x) for x in output.getvalue()]
