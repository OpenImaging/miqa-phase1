import datetime
from girder import events, plugin
from girder.models.user import User

from .session import Session
from .email import Email
from .result import Result

class GirderPlugin(plugin.GirderPlugin):
    DISPLAY_NAME = 'miqa server'

    def load(self, info):
        info['apiRoot'].miqa = Session()
        info['apiRoot'].miqa_email = Email()
        info['apiRoot'].result = Result()
