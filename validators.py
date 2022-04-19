import os
from ttkbootstrap.validation import validator, ValidationEvent, add_validation

@validator
def _validatePath(event:ValidationEvent):
    """Contents is a valid os path."""
    if os.path.exists(event.postchangetext):
        return True
    else:
        return False

@validator
def _validateFileType(event:ValidationEvent, filetypes=None):
    """Contents is a valid os path to a file of a type thats included in `filetypes`"""

    fileExtension = event.postchangetext.split('.')[-1]

    if os.path.exists(event.postchangetext) and fileExtension in filetypes:
        return True
    else:
        return False

@validator
def _validateEmail(event:ValidationEvent):
    """Contents is a valid email"""
    if '@' in event.postchangetext and '.' in event.postchangetext:
        return True
    else:
        return False

def addPathValidation(widget, when="focusout"):
    """Check if widget contents is a valid os path. Sets the state to 'Invalid'
    if not an os path.

    Parameters:

        widget (Widget):
            The widget on which to add validation.

        when (str):
            Specifies when to apply validation. See the `add_validation`
            method docstring for a full list of options.
    """
    add_validation(widget, _validatePath, when=when)

def addFileTypeValidation(widget, when="focusout", filetypes:set=None):
    """Check if widget contents is a valid os path to a file of a type thats 
    included n `filetypes`. Sets the state to 'Invalid' if not an os path.

    Parameters:

        widget (Widget):
            The widget on which to add validation.

        when (str):
            Specifies when to apply validation. See the `add_validation`
            method docstring for a full list of options.
    """
    add_validation(widget, _validateFileType, when=when, filetypes=filetypes)

def addEmailValidation(widget, when="focusout"):
    """Check if widget contents is a valid email. Sets the state to
    'Invalid' if not an os path.

    Parameters:

        widget (Widget):
            The widget on which to add validation.

        when (str):
            Specifies when to apply validation. See the `add_validation`
            method docstring for a full list of options.
    """
    add_validation(widget, _validateEmail, when=when)