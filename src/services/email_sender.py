import os
import base64

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.application import MIMEApplication
import mimetypes



class EmailSender:
    """
    EmailSender serves as the entrypoint for the Gmail service API.
    Gmail service API documentation:
    https://developers.google.com/gmail/api/reference/rest

    Args:
        client_secret_file: The name of the user's client secret file.

    Attributes:
        client_secret_file (str): The name of the user's client secret file.
        service (googleapiclient.discovery.Resource): The Gmail service object.
    """

    _SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    _API_NAME = 'gmail'
    _API_VERSION = 'v1'
    _USER_ID = 'me'

    # If you don't have a client secret file, follow the instructions at:
    # https://developers.google.com/gmail/api/quickstart/python
    # Make sure the client secret file is in the root directory of your app.

    def __init__(
        self,
        client_secret_file: str = 'client_secret.json',
        creds_file: str = 'gmail_token.json',
        _creds: Credentials | None = None
    ) -> None:
        """ Initializes EmailSender. Creates a googleapiclient.discovery resource
        for interacting with the Gmail API from a client secret file.

        Args:
            client_secret_file: The filename of the client secret file.
            creds_file: The serialized creds file that stores the user's
                access and refresh tokens.
            _creads: The credentials to use.

        Raises:
            FileNotFoundError: Could not find the requested file.
        """

        self.client_secret_file = client_secret_file
        self.creds_file = creds_file
        self.creds : Credentials = None

        try:
            # The file gmail_token.json stores the user's access and refresh
            # tokens, and is created automatically when the authorization flow
            # completes for the first time.
            if _creds is not None:
                self.creds = _creds
            elif os.path.exists(self.creds_file):
                self.creds = Credentials.from_authorized_user_file(
                    self.creds_file,
                    self._SCOPES
                )

            if self.creds is None or not self.creds.valid:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.client_secret_file,
                    self._SCOPES
                )
                self.creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open(creds_file, 'w') as token:
                    token.write(self.creds.to_json())

        except ValueError:
            raise FileNotFoundError(
                "Your 'client_secret.json' file is nonexistent. Make sure "
                "the file is in the root directory of your application. If "
                "you don't have a client secrets file, go to https://"
                "developers.google.com/gmail/api/quickstart/python, and "
                "follow the instructions listed there."
            )

        try:
            self._service = build(
                self._API_NAME,
                self._API_VERSION,
                credentials=self.creds
            )

        except HttpError as error:
            message = 'Could not build googleapiclient.discovery service'\
                      f'for the {self._API_NAME}-{self._API_VERSION} API!'\
                      f'Error: {error}'
            print(message)

    @property
    def service(self) -> Resource:
        # Since the token is only used through calls to the service object,
        # this ensure that the token is always refreshed before use.
        if self.creds.expired and self.creds.refresh_token:
            self.creds.refresh(Request())

        return self._service

    def send_email(
        self,
        sender: str,
        to: str,
        subject: str = '',
        msg_html: str | None = None,
        msg_plain: str | None = None,
        cc: list[str] | None = None,
        bcc: list[str] | None = None,
        attachments: list[str] | None = None
    ) -> dict[str, str]:
        """ Creates and sends the raw email message.

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

        Returns:
            The message dict.
        """

        msg = self.create_message(
            sender,
            to,
            subject,
            msg_html,
            msg_plain,
            cc,
            bcc,
            attachments
        )

        res = self.send_message(msg)
        return res

    def create_message(
        self,
        sender: str,
        to: str,
        subject: str = '',
        msg_html: str | None = None,
        msg_plain: str | None = None,
        cc: list[str] | None = None,
        bcc: list[str] | None = None,
        attachments: list[str] | None = None
    ) -> dict[str, MIMEMultipart]:
        """ Creates the raw email message to be sent.

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

        Returns:
            The message dict.
        """

        msg = MIMEMultipart('mixed' if attachments else 'alternative')
        msg['To'] = to
        msg['From'] = sender
        msg['Subject'] = subject

        if cc:
            msg['Cc'] = ', '.join(cc)

        if bcc:
            msg['Bcc'] = ', '.join(bcc)

        if msg_html is None:
            msg_html = ''

        msg_html += "<br/><br/>"

        attach_plain = MIMEMultipart('alternative') if attachments else msg
        attach_html = MIMEMultipart('related') if attachments else msg

        if msg_plain:
            attach_plain.attach(MIMEText(msg_plain, 'plain'))

        if msg_html:
            attach_html.attach(MIMEText(msg_html, 'html'))

        if attachments:
            attach_plain.attach(attach_html)
            msg.attach(attach_plain)
            self._add_attachments(msg, attachments)

        return {
            'raw': base64.urlsafe_b64encode(msg.as_string()
                .encode('utf-8')).decode('utf-8')
        }

    def send_message(
        self,
        message: dict[str, MIMEMultipart]
    ) -> dict[str, str]:
        """ Sends the provided message.

        Args:
            message: The message to send.

        Raises:
            googleapiclient.errors.HttpError: An Http error has occured.
        """

        req = self.service.users().messages().send(
            userId=self._USER_ID,
            body=message
        )
        res = req.execute()
        return res

    def _add_attachments(
        self,
        msg: MIMEMultipart,
        attachments: list[str]
    ) -> None:
        """ Converts attachment filepaths to MIME objects and adds them to msg.

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
