import datetime
from girder import events, plugin
from girder.models.user import User

from miqa import Miqa

class GirderPlugin(plugin.GirderPlugin):
    DISPLAY_NAME = 'miqa server'

    def load(self, info):
        info['apiRoot'].miqa = Miqa()
