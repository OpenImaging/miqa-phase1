import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import mimetypes
from urllib.parse import quote
import uuid

from girder import events
from girder.api.rest import Resource
from girder.api import access, rest
from girder.api.describe import Description, autoDescribeRoute
from girder.constants import SettingKey
from girder.exceptions import RestException
from girder.models.setting import Setting


class MiqaEmail(Resource):
    def __init__(self):
        super(MiqaEmail, self).__init__()
        self.resourceName = 'miqa_email'

        self.route('POST', (), self.sendEmail)

    @access.user
    @autoDescribeRoute(
        Description('')
        .jsonParam('message', 'A JSON object containing the metadata keys to add',
                   paramType='body', requireObject=True)
        .errorResponse())
    def sendEmail(self, message, params):
        msg = MIMEMultipart('related')
        msg['From'] = Setting().get(SettingKey.EMAIL_FROM_ADDRESS, 'Girder <no-reply@girder.org>')
        msg['To'] = message['to']
        msg['Subject'] = message['subject']
        body = message['body']
        image_content_ids = []
        images_html = []
        alternative = MIMEMultipart('alternative')
        msg.attach(alternative)

        for screenshot in message['screenshots']:
            dataURL = screenshot['dataURL']
            name = screenshot['name']
            encoded = dataURL[dataURL.find(',')+1:]
            mime = dataURL[dataURL.find(':')+1:dataURL.find(';')]
            image = MIMEImage(base64.b64decode(encoded), name=name)
            content_id = str(uuid.uuid4())
            image.add_header('Content-ID', f'<{content_id}>')
            image.add_header('Content-Disposition',
                             f'attachment; filename="{name}{getExtension(mime)}"')
            images_html.append(f'<img src="cid:{content_id}" /><br /><div>{name}</div>')
            msg.attach(image)
            image_content_ids.append(content_id)

        alternative.attach(MIMEText(body))
        alternative.attach(MIMEText(f"""\
{''.join([f'<p>{line}</p>' for line in body.splitlines()])}
<br />
{'<br />'.join(images_html)}
""", 'html'))

        events.daemon.trigger('_sendmail', info={
            'message': msg,
            'recipients': [message['to']]
        })


def getExtension(mime):
    if mime == 'image/jpeg':
        return '.jpg'
    elif mime == 'image/png':
        return '.png'
    return ''
