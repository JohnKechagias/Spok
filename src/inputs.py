from pathlib import Path
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tktooltip import ToolTip
from tkinter import filedialog as fd

from widgets.image_button import ImageButton
import widgets.validation.validators as validators
from widgets.placeholder_entry import PlaceholderEntry



class InfoInput(ttk.Labelframe):
    def __init__(
        self,
        master,
        templates_path: Path,
        userlists_path: Path,
        testmode: bool = True
    ) -> None:
        super().__init__(master, text='Certificate Options', padding=(16, 10))

        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        self.templates_path = templates_path
        self.userlists_path = userlists_path

        self.font = '-size 13'

        self.image_path = ttk.StringVar()
        self.info_file_path = ttk.StringVar()

        self.image_path.trace_add('write', self._invoke_image_handler)
        self.info_file_path.trace_add('write', self._invoke_info_file_handler)

        self.test_mode = ttk.BooleanVar(value=testmode)

        # Manually call the handlers instead of tracing the vars because
        # we want to call the handlers whenever the complete path is given
        # and not when the path changes.

        # Ex. if a user types the path into the Entry the stringVar will
        # constantly change and the handler will be called multiple
        # times with an incompete path. To avoid this we will decide when
        # to call the handler
        self.image_changed_handler = None
        self.info_file_changed_handler = None

        self.select_template_button = ImageButton(
            master=self,
            default_image='template-default',
            active_image='template-active',
            command=self._select_image_file
        )
        self.select_template_button.grid(row=0, column=0, padx=(0, 16), pady=4, sticky=W)
        msg = 'The image file to write on.'
        ToolTip(self.select_template_button, msg=msg, delay=1)

        self.image_path_entry = ttk.Entry(
            master=self,
            font=self.font,
            textvariable=self.image_path
        )
        self.image_path_entry.grid(row=0, column=1, columnspan=3, pady=6, sticky=EW)

        self.image_path_entry.bind('<Return>', lambda _: self._invoke_image_handler(), add='+')

        validators.add_file_type_validation(self.image_path_entry,
            filetypes={'img', 'png', 'jpeg', 'jpg'})

        self.select_info_file_button = ImageButton(
            master=self,
            default_image='userlist-default',
            active_image='userlist-active',
            command=self._select_info_file
        )
        msg = 'The info file to get the names and emails from.'
        ToolTip(self.select_info_file_button, msg=msg, delay=1)

        self.select_info_file_button.grid(row=1, column=0, padx=(0, 16), pady=4, sticky=W)

        self.info_path_entry = ttk.Entry(
            master=self,
            font=self.font,
            textvariable=self.info_file_path
        )
        self.info_path_entry.grid(row=1, column=1, columnspan=3, pady=6, sticky=EW)

        self.info_path_entry.bind('<Return>', lambda _: self._invoke_info_file_handler(), add='+')

        validators.add_file_type_validation(self.info_path_entry,
            filetypes={'txt', 'exel', 'xlsx'})

        ttk.Separator(self).grid(row=2, column=0, columnspan=3, pady=10, sticky=EW)

        self.error_checking_mode_checkbutton = ttk.Checkbutton(
            master=self,
            bootstyle=(WARNING, TOGGLE, SQUARE),
            text=' Test Mode',
            variable=self.test_mode
        )
        self.error_checking_mode_checkbutton.grid(row=3, column=0, columnspan=2, sticky=W, pady=6)

        self.create_certificates_button = ttk.Button(
            master=self,
            bootstyle=(DANGER, OUTLINE),
            text='Create Certificates',
            padding=9, width=18,
        )
        self.create_certificates_button.grid(row=3, rowspan=2, column=2, sticky=E)

    def _select_image_file(self):
        image_path = fd.askopenfilename(
            title='Select template',
            filetypes=(("Image files",".img .png .jpeg .jpg"),("All files","*.*")),
            initialdir=self.templates_path
        )

        if image_path not in {None, '', ()}:
            self.image_path.set(image_path)

    def _select_info_file(self):
        info_file_path = fd.askopenfilename(
            title='Select Info file',
            filetypes=(("Info files",".txt .exel .xlsx .csv"),("All files","*.*")),
            initialdir=self.userlists_path
        )

        if info_file_path not in {None, '', ()}:
            self.info_file_path.set(info_file_path)

    def _invoke_image_handler(self, *_):
        if self.image_changed_handler is not None and self.image_path_entry.validate():
            self.image_changed_handler(self.image_path.get())

    def _invoke_info_file_handler(self, *_):
        if self.info_file_changed_handler is not None and self.info_path_entry.validate():
            self.info_file_changed_handler(self.info_file_path.get())


class EmailInput(ttk.Labelframe):
    def __init__(
        self,
        master,
        testemail: str = 'testEmail@something.com',
        realemail: str = 'realEmail@something.com',
        testmode: bool = True
    ) -> None:
        super().__init__(master, text='Emailing Options', padding=(16, 10))

        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        self.font = '-size 13'

        self.test_email = ttk.StringVar(value=testemail)
        self.real_email = ttk.StringVar(value=realemail)

        self.test_mode = ttk.BooleanVar(value=testmode)

        self.test_email_button = ImageButton(
            master=self,
            default_image='test-email-default',
            active_image='test-email-active'
        )
        self.test_email_button.grid(row=0, column=0, padx=(0, 16), pady=4, sticky=W)
        msg = 'The email to use in test mode.'
        ToolTip(self.test_email_button, msg=msg, delay=1)

        self.test_email_entry = PlaceholderEntry(
            master=self,
            placeholder='Testing Email',
            font=self.font,
            textvariable=self.test_email
        )
        self.test_email_entry.grid(row=0, column=1, columnspan=2, pady=6, sticky=EW)
        self.test_email_entry.bind('<Return>',
            lambda _: self.test_email_entry.validate(), add='+')
        validators.add_email_validation(self.test_email_entry)

        self.real_email_button = ImageButton(
            master=self,
            default_image='email-default',
            active_image='email-active'
        )
        self.real_email_button.grid(row=1, column=0, padx=(0, 16), pady=4, sticky=W)
        msg = 'The email to use when sending certificates.'
        ToolTip(self.real_email_button, msg=msg, delay=1)

        self.real_email_entry = PlaceholderEntry(
            master=self,
            bootstyle=(WARNING),
            placeholder='Real Email',
            font=self.font,
            textvariable=self.real_email
        )
        self.real_email_entry.grid(row=1, column=1, columnspan=2, pady=6, sticky=EW)
        self.real_email_entry.bind('<Return>',
            lambda _: self.real_email_entry.validate(), add='+')
        validators.add_email_validation(self.real_email_entry)

        ttk.Separator(self).grid(row=2, column=0, columnspan=3, pady=10, sticky=EW)

        self.test_mode_checkbutton = ttk.Checkbutton(
            master=self,
            bootstyle=(DANGER, TOGGLE, SQUARE),
            text=' Test Mode',
            variable=self.test_mode
        )
        self.test_mode_checkbutton.grid(row=3, column=0, columnspan=2, sticky=W, pady=6)

        self.send_emails_button = ttk.Button(
            master=self,
            bootstyle=(DANGER, OUTLINE),
            text='Send Emails',
            padding=9, width=18,
        )
        self.send_emails_button.grid(row=3, rowspan=2, column=2, sticky=E)
