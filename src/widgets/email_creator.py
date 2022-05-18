from typing import Dict

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from .placeholder_entry import PlaceholderEntry



class EmailCreator(ttk.Frame):
    def __init__(self, master=None, *args, **kwargs):
        super().__init__(master, padding=10)

        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)

        # Default behavior is batch sending of emails.
        # Disables batch sending and enables the sending
        # of personal emails (with a single recipient).
        self.personal_email = ttk.BooleanVar(value=False)
        self.personal_email.trace_add('write', self.personal_email_changed)
        self.email_signature = ''

        self._subject = PlaceholderEntry(self, placeholder='Subject')
        self._subject.grid(row=1,  column=0, sticky=EW, pady=(0, 5))

        self._receiver = PlaceholderEntry(self, placeholder='To')

        self._body = ttk.Text(self, *args, **kwargs)
        self._body.grid(row=2,  column=0, sticky=NSEW, pady=(5, 0))

        self._body.bind('<KeyPress-t>', lambda _: self.get_email())

    def personal_email_changed(self, *args):
        if self.personal_email.get():
            self._receiver.grid(row=0,  column=0, sticky=EW, pady=(5,10))
        else:
            self._receiver.grid_remove()

    def get_email(self) -> Dict[str, str]:
        """Returns the email info in a form of a dict.
        Email info consists of the title, the recipient and the body of
        the email in HTML form. If the personalEmail flag is false, the
        recipient is empty.

        Returns:
            dict: email info
        """
        email = {}
        email['subject'] = self._subject.get()

        recipient = ''
        if self.personal_email:
            recipient = self._receiver.get()
        email['to'] = recipient

        signature = self.get_signature()
        body = self._body.get('1.0', END)
        body = body.replace('\n', '<br>')
        body = '<html><head></head><body><p style="color:black">' + body +\
        signature + '</p></body></html>'

        email['body'] = body
        return email

    def get_signature(self):
        with open('emailSignature.html', 'r') as file:
            signature = file.read()
        return signature
