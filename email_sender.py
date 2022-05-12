# =-=-=-=-=-=-=-=- Imports -=-=-=-=-=-=-=-=-=
import os
import base64

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
import mimetypes
from .google import create_service


# =-=-=-=-=-=-=- Global Vars -=-=-=-=-=-=-=-=

CLIENT_SECRET_FILE = 'client_secret.json'
API_NAME = 'gmail'
API_VERSION = 'v1'
SCOPES = ['https://mail.google.com/']

user_ID = 'me'
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=


def get_email_service():
    return create_service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

def send_message(Service, message):
    """ sends the provided message. If the sending was succesful
    it prints the message ID """

    try:
        message = Service.users().messages().send(userId=user_ID, body=message).execute()
        print('message ID: {}'.format(message['id']))
        return message
    except Exception as e:
        print(f'an error occured: {e}')
        return None

def create_message_with_attachments(to:str, sender:str, subject:str, body:str, files:list) -> dict:
    # create the MIME message
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

        if maintype == 'text':
            with open(attachment, 'rb') as f:
                msg = MIMEText(f.read().decode('utf-8'), _subtype=subtype)

        elif maintype == 'image':
            with open(attachment, 'rb') as f:
                msg = MIMEImage(f.read(), _subtype=subtype)

        elif maintype == 'audio':
            with open(attachment, 'rb') as f:
                msg = MIMEAudio(f.read(), _subtype=subtype)

        else:
            with open(attachment, 'rb') as f:
                msg = MIMEBase(maintype, subtype)
                msg.set_payload(f.read())

        msg.add_header('Content-Disposition', 'attachment', filename=filename)
        mime_message.attach(msg)

    rawMsg = base64.urlsafe_b64encode(mime_message.as_string().encode('utf-8'))
    return {'raw': rawMsg.decode('utf-8')}


def create_message_without_attachments(to:str, sender:str, subject:str, body:str) -> dict:
    # create the MIME message
    mimeMessage = MIMEMultipart()
    mimeMessage['to'] = to
    mimeMessage['from'] = sender
    mimeMessage['subject'] = subject
    mimeMessage.attach(MIMEText(body, 'html'))

    rawMsg = base64.urlsafe_b64encode(mimeMessage.as_string().encode('utf-8'))
    return {'raw': rawMsg.decode('utf-8')}
