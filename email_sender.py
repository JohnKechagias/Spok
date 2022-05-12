import os
import base64

from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
import mimetypes
import google_service


CLIENT_SECRET_FILE = 'client_secret.json'
API_NAME = 'gmail'
API_VERSION = 'v1'
SCOPES = ['https://mail.google.com/']
USER_ID = 'me'


class EmailSender:
    client_secret_filename = CLIENT_SECRET_FILE
    api_name = API_NAME
    api_version = API_VERSION
    scopes = SCOPES
    service = None

    @classmethod
    def initialize_service(cls) -> None:
        cls.service = google_service.create_service(
            cls.client_secret_filename,
            cls.api_name,
            cls.api_version,
            cls.scopes
        )

    @classmethod
    def send_email(cls, to, sender, subject, body, files=None) -> None:
        msg = EmailSender.create_message(to, sender, subject, body, files)
        EmailSender.send_message(cls.service, msg)

    @staticmethod
    def send_message(service, message):
        """ sends the provided message. If the sending was succesful
        it prints the message ID """

        try:
            message = service.users().messages().send(userId=USER_ID, body=message).execute()
            print('message ID: {}'.format(message['id']))
            return message
        except Exception as e:
            print(f'an error occured: {e}')
            return None

    @staticmethod
    def create_message(
        to:str,
        sender:str,
        subject:str,
        body:str,
        files:list|tuple=None
        ) -> dict:
        mime_message = MIMEMultipart()
        mime_message['to'] = to
        mime_message['from'] = sender
        mime_message['subject'] = subject
        mime_message.attach(MIMEText(body, 'html'))
        """pdf shit
        for attachment in files:
            # open the file in bynary
            binary_pdf = open(attachment, 'rb')

            payload = MIMEBase('application', 'octate-stream', Name=attachment)
            payload.set_payload((binary_pdf).read())

            # enconding the binary into base64
            encoders.encode_base64(payload)

            # add header with pdf name
            payload.add_header('Content-Decomposition', 'attachment', filename=attachment)
            mimeMessage.attach(payload)

            rawMsg = base64.urlsafe_b64encode(mimeMessage.as_string().encode('utf-8'))
            return {'raw': rawMsg.decode('utf-8')}"""

        for attachment in files:
            (contenttype, encoding) = mimetypes.guess_type(attachment)

            if contenttype is None or encoding is not None:
                contenttype = 'application/octet-stream'

            (maintype, subtype) = contenttype.split('/', 1)
            filename = os.path.basename(attachment)
            print(maintype, subtype)

            if maintype == 'text':
                with open(attachment, 'rb') as f:
                    msg = MIMEText(f.read().decode('utf-8'), _subtype=subtype)
            elif maintype == 'image':

                with open(attachment, 'rb') as f:
                    msg = MIMEImage(f.read(), _subtype=subtype)
            elif maintype == 'audio':

                with open(attachment, 'rb') as f:
                    msg = MIMEAudio(f.read(), _subtype=subtype)

            elif maintype=='application' and subtype=='pdf':
                # open the file in bynary
                binary_pdf = open(attachment, 'rb')
                msg = MIMEBase('application', 'octate-stream', Name=attachment)
                msg.set_payload((binary_pdf).read())
                # enconding the binary into base64
                encoders.encode_base64(msg)

            else:
                with open(attachment, 'rb') as f:
                    msg = MIMEBase(maintype, subtype)
                    msg.set_payload(f.read())

            msg.add_header('Content-Disposition', 'attachment', filename=filename)
            mime_message.attach(msg)

        rawMsg = base64.urlsafe_b64encode(mime_message.as_string().encode('utf-8'))
        return {'raw': rawMsg.decode('utf-8')}
