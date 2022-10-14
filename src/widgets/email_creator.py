from typing import Dict

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from .placeholder_entry import PlaceholderEntry



class EmailCreator(ttk.Frame):
    def __init__(self, master=None, subject='', body='', *args, **kwargs):
        super().__init__(master, padding=10)

        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)

        # Default behavior is batch sending of emails.
        # Disables batch sending and enables the sending
        # of personal emails (with a single recipient).
        self.personal_email = ttk.BooleanVar(value=False)
        self.personal_email.trace_add('write', self._on_personal_email_bool_changed)

        try:
            with open('emailSignature.html', 'r', encoding='UTF-8') as file:
                signature = file.read()
        except FileNotFoundError:
            signature = ''
        finally:
            self.signature = signature

        self._subject = PlaceholderEntry(self, placeholder='Subject', text=subject)
        self._subject.grid(row=1, column=0, sticky=EW, pady=(0, 5))

        self._to = PlaceholderEntry(self, placeholder='To')

        self._body = ttk.Text(self, *args, **kwargs, undo=True)
        self._body.grid(row=2,  column=0, sticky=NSEW, pady=(5, 0))
        self._body.insert(END, body.strip())

        self._body.bind('<KeyPress-t>', lambda _: self.get_email())

    def _on_personal_email_bool_changed(self, *args):
        if self.personal_email.get():
            self._to.grid(row=0,  column=0, sticky=EW, pady=(5,10))
        else:
            self._to.grid_remove()

    def get_email(self) -> Dict[str, str]:
        """ Return the email info in a form of a dict.
        Email info consists of the title, the recipient and the body of
        the email in HTML form. If the personalEmail flag is false, the
        recipient is empty.

            Returns:
                dict: email info
        """
        email = {}
        email['subject'] = self._subject.get()

        to = ''
        if self.personal_email:
            to = self._to.get()
        email['to'] = to

        body = self._body.get('1.0', END)
        body = body.replace('\n', '<br>')
        body = '<html><head></head><body><p style="color:black">' + body +\
        self.signature + '</p></body></html>'

        email['body'] = body
        return email

    def get_subject(self) -> str:
        return self._subject.get()

    def get_body(self) -> str:
        return self._body.get('1.0', END)
