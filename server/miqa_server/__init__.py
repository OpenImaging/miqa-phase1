import datetime
from girder import events, plugin
from girder.models.user import User

from .client_webroot import ClientWebroot
from .session import Session
from .email import Email
from .setting import SettingResource


class GirderPlugin(plugin.GirderPlugin):
    DISPLAY_NAME = 'miqa server'

    def load(self, info):
        # Relocate Girder
        info['serverRoot'], info['serverRoot'].girder = (ClientWebroot(),
                                                         info['serverRoot'])
        info['serverRoot'].api = info['serverRoot'].girder.api

        info['apiRoot'].miqa = Session()
        info['apiRoot'].miqa_email = Email()
        info['apiRoot'].miqa_setting = SettingResource()
