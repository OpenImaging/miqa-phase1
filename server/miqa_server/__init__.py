import datetime
from girder import events, logger, plugin
from girder.models.user import User
from girder.utility import server

from .client_webroot import ClientWebroot
from .session import Session
from .email import Email
from .setting import SettingResource
from .learning import Learning


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
        info['apiRoot'].learning = Learning()

        events.bind('jobs.job.update.after', 'active_learning', afterJobUpdate)


def afterJobUpdate(event):
    # learned from https://github.com/girder/large_image/blob/girder-3/girder/girder_large_image/__init__.py#L83
    # logger.info('afterJobUpdate event triggered')
    job = event.info['job']
    meta = job.get('meta', {})
    if (meta.get('creator') != 'miqa' or not meta.get('itemId') or
            meta.get('task') != 'learning_with_data'):
        # logger.info('Ignoring unknown event: {0}'.format())
        return
    # logger.info('Calling Learning.afterJobUpdate()')
    Learning.afterJobUpdate(job)
