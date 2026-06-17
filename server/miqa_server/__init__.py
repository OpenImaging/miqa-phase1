import datetime
import smtplib
from girder import logger
from girder.utility import mail_utils
from girder import events, plugin
from girder.models.user import User
from girder.utility import server

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

        _orig_init = smtplib.SMTP.__init__

        def debug_smtp_init(self, *args, **kwargs):
            _orig_init(self, *args, **kwargs)
            self.set_debuglevel(1)

        smtplib.SMTP.__init__ = debug_smtp_init

        original_send = mail_utils._SMTPConnection.send
        original_enter = mail_utils._SMTPConnection.__enter__

        def debug_enter(self):
            logger.info(
                'SMTP debug: connecting host=%r port=%r encryption=%r username=%r',
                self.host, self.port, self.encryption, self.username
            )
            return original_enter(self)

        def debug_send(self, fromAddress, toAddresses, message):
            logger.info(
                'SMTP debug: sending from=%r to=%r message_len=%d',
                fromAddress, toAddresses, len(message)
            )
            try:
                result = original_send(self, fromAddress, toAddresses, message)
                logger.info('SMTP debug: sendmail completed: %r', result)
                return result
            except Exception:
                logger.exception('SMTP debug: sendmail failed')
                raise

        mail_utils._SMTPConnection.__enter__ = debug_enter
        mail_utils._SMTPConnection.send = debug_send

server.getStaticRoot = lambda: 'static'
