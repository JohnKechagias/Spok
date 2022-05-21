import os
import base64
from typing import List, Optional

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.application import MIMEApplication
import mimetypes
import google_service


CLIENT_SECRET_FILE = 'client_secret.json'
API_NAME = 'gmail'
API_VERSION = 'v1'
SCOPES = ['https://www.googleapis.com/auth/gmail.send']
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

    @classmethod
    def send_message(cls, message):
        """
        Send the provided message. If the sending was succesful,
        print the message ID.
        """

        try:
            message = cls.service.users().messages().send(userId=USER_ID, body=message).execute()
            print('message ID: {}'.format(message['id']))
            return message
        except Exception as e:
            print(f'an error occured: {e}')
            return None

    @staticmethod
    def create_message(
        sender: str,
        to: str,
        subject: str,
        body: str,
        attachments: Optional[List[str]] = None
    ) -> dict:
        """
        Creates the raw email message to be sent.

        Args:
            sender: The email address the message is being sent from.
            to: The email address the message is being sent to.
            subject: The subject line of the email.
            msg_html: The HTML message of the email.
            msg_plain: The plain text alternate message of the email (for slow
                or old browsers).
            cc: The list of email addresses to be Cc'd.
            bcc: The list of email addresses to be Bcc'd
            attachments: A list of attachment file paths.
            signature: Whether the account signature should be added to the
                message. Will add the signature to your HTML message only, or a
                create a HTML message if none exists.

        Returns:
            The message dict.

        """

        msg = MIMEMultipart()
        msg['to'] = to
        msg['from'] = sender
        msg['subject'] = subject
        msg.attach(MIMEText(body, 'html'))

        if attachments:
            EmailSender._add_attachments(msg, attachments)

        rawMsg = base64.urlsafe_b64encode(
            msg.as_string().encode('utf-8'))
        return {'raw': rawMsg.decode('utf-8')}

    @staticmethod
    def _add_attachments(
        msg: MIMEMultipart,
        attachments: List[str]
    ) -> None:
        """
        Converts attachment filepaths to MIME objects and adds them to msg.

        Args:
            msg: The message to add attachments to.
            attachments: A list of attachment file paths.

        """

        for attachment in attachments:
            content_type, encoding = mimetypes.guess_type(attachment)

            if content_type is None or encoding is not None:
                content_type = 'application/octet-stream'

            main_type, sub_type = content_type.split('/', 1)
            filename = os.path.basename(attachment)

            with open(attachment, 'rb') as file:
                raw_data = file.read()

                attm : MIMEBase
                if main_type == 'text':
                    attm = MIMEText(raw_data.decode('utf-8'), _subtype=sub_type)
                elif main_type == 'image':
                    attm = MIMEImage(raw_data, _subtype=sub_type)
                elif main_type == 'audio':
                    attm = MIMEAudio(raw_data, _subtype=sub_type)
                elif main_type == 'application':
                    attm = MIMEApplication(raw_data, _subtype=sub_type)
                else:
                    attm = MIMEBase(main_type, sub_type)
                    attm.set_payload(raw_data)

            attm.add_header('Content-Disposition', 'attachment', filename=filename)
            msg.attach(attm)