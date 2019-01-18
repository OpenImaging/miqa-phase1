import datetime
from girder import events, plugin
from girder.models.user import User

from .miqa import Miqa
from .miqa_email import MiqaEmail

class GirderPlugin(plugin.GirderPlugin):
    DISPLAY_NAME = 'miqa server'

    def load(self, info):
        info['apiRoot'].miqa = Miqa()
        info['apiRoot'].miqa_email = MiqaEmail()
