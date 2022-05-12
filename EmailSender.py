# =-=-=-=-=-=-=-=- Imports -=-=-=-=-=-=-=-=-=
import os
import base64
from email import encoders

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
import mimetypes
from Google import CreateService


# =-=-=-=-=-=-=- Global Vars -=-=-=-=-=-=-=-=

CLIENT_SECRET_FILE = 'client_secret.json'
API_NAME = 'gmail'
API_VERSION = 'v1'
SCOPES = ['https://mail.google.com/']

userID = 'me'
listOfEmailingInfo = []
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=


def GetEmailService():
    return CreateService(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

def SendMessage(Service, message):
    """ sends the provided message. If the sending was succesful
    it prints the message ID """
    
    try:
        message = Service.users().messages().send(userId=userID, body=message).execute()
        print('message ID: {}'.format(message['id']))
        return message
    except Exception as e:
        print(f'an error occured: {e}')
        return None

def CreateMessageWithAttachments(to:str, sender:str, subject:str, body:str, files:list) -> dict:
    # create the MIME message
    mimeMessage = MIMEMultipart()
    mimeMessage['to'] = to
    mimeMessage['from'] = sender
    mimeMessage['subject'] = subject
    mimeMessage.attach(MIMEText(body, 'html'))
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
        (contentType, encoding) = mimetypes.guess_type(attachment)
    
        if contentType is None or encoding is not None:
            contentType = 'application/octet-stream'
    
        (mainType, subType) = contentType.split('/', 1)
        filename = os.path.basename(attachment)

        if mainType == 'text':
            with open(attachment, 'rb') as f:
                msg = MIMEText(f.read().decode('utf-8'), _subtype=subType)
        
        elif mainType == 'image':
            with open(attachment, 'rb') as f:
                msg = MIMEImage(f.read(), _subtype=subType)     
                
        elif mainType == 'audio':
            with open(attachment, 'rb') as f:
                msg = MIMEAudio(f.read(), _subtype=subType)  
                
        else:
            with open(attachment, 'rb') as f:
                msg = MIMEBase(mainType, subType)
                msg.set_payload(f.read())
                
        msg.add_header('Content-Disposition', 'attachment', filename=filename)
        mimeMessage.attach(msg)
    
    rawMsg = base64.urlsafe_b64encode(mimeMessage.as_string().encode('utf-8'))
    return {'raw': rawMsg.decode('utf-8')}
        

def CreateMessageWithoutAttachments(to:str, sender:str, subject:str, body:str) -> dict:
    # create the MIME message
    mimeMessage = MIMEMultipart()
    mimeMessage['to'] = to
    mimeMessage['from'] = sender
    mimeMessage['subject'] = subject
    mimeMessage.attach(MIMEText(body, 'html'))
        
    rawMsg = base64.urlsafe_b64encode(mimeMessage.as_string().encode('utf-8'))
    return {'raw': rawMsg.decode('utf-8')}
    
def EmailingListFromTxt(txtPath:str) -> list:
    """ Converts a txt file to an emailing list. Txt structure is
    "email fileLocation" """
    emailingInfoList = []
    try:
        # read from attendants
        with open(txtPath, "r", encoding='utf-8') as file:
            lines = file.readlines()
            
        for line in lines:
            temp = line.replace('\n', '').split(' ', 1)
            emailingInfo = {'email': temp[0], 'fileLocation': temp[1]}
            emailingInfoList.append(emailingInfo)
    except IOError:
        print("Could not find txt file.")
        
    return emailingInfoList
        
def EmailingListFromEmailTxt(txtPath:str) -> list:
    """ Converts a txt file to an emailing list. Txt structure is
    "email fileLocation" """
    emailingInfoList = []
    try:
        # read from attendants
        with open(txtPath, "r", encoding='utf-8') as file:
            lines = file.readlines()
            
        for line in lines:
            temp = line.replace('\n', '').replace(' ', '')
            if temp != '':
                emailingInfoList.append(temp)
            
    except IOError:
        print("Could not find txt file.")
        
    return emailingInfoList