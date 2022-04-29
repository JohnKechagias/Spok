import os
from ttkbootstrap.validation import validator, ValidationEvent, add_validation

@validator
def _validate_path(event:ValidationEvent):
    """Contents is a valid os path."""
    if os.path.exists(event.postchangetext):
        return True
    else:
        return False

@validator
def _validate_file_type(event:ValidationEvent, filetypes=None):
    """Contents is a valid os path to a file of a type thats included in `filetypes`"""

    fileExtension = event.postchangetext.split('.')[-1]

    if os.path.exists(event.postchangetext) and fileExtension in filetypes:
        return True
    else:
        return False

@validator
def _validate_email(event:ValidationEvent):
    """Contents is a valid email"""
    if '@' in event.postchangetext and '.' in event.postchangetext:
        return True
    else:
        return False

def add_path_validation(widget, when="focusout"):
    """Check if widget contents is a valid os path. Sets the state to 'Invalid'
    if not an os path.

    Parameters:

        widget (Widget):
            The widget on which to add validation.

        when (str):
            Specifies when to apply validation. See the `add_validation`
            method docstring for a full list of options.
    """
    add_validation(widget, _validate_path, when=when)

def add_file_type_validation(widget, when="focusout", filetypes:set=None):
    """Check if widget contents is a valid os path to a file of a type thats
    included n `filetypes`. Sets the state to 'Invalid' if not an os path.

    Parameters:

        widget (Widget):
            The widget on which to add validation.

        when (str):
            Specifies when to apply validation. See the `add_validation`
            method docstring for a full list of options.
    """
    add_validation(widget, _validate_file_type, when=when, filetypes=filetypes)

def add_email_validation(widget, when="focusout"):
    """Check if widget contents is a valid email. Sets the state to
    'Invalid' if not an os path.

    Parameters:

        widget (Widget):
            The widget on which to add validation.

        when (str):
            Specifies when to apply validation. See the `add_validation`
            method docstring for a full list of options.
    """
    add_validation(widget, _validate_email, when=when)