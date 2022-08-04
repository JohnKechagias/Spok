import os
import threading
import multiprocessing as mp
from pathlib import Path
from functools import partial

import tkinter as tk
from tkinter import Misc, filedialog as fd
from tkinter.font import ROMAN
from typing import Any, Callable, List, Optional

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs.dialogs import FontDialog, Messagebox

from tktooltip import ToolTip

from certificate_creation import CertificateCreator
from email_sender import EmailSender

from widgets.logger import Logger
from widgets.canvas_image import ImageViewer
from widgets.color_selector import ColorSelector
from widgets.data_viewer import DataViewer
from widgets.email_creator import EmailCreator
from widgets.placeholder_entry import PlaceholderEntry
from widgets.text_editor import TextEditor
from widgets.image_button import ImageButton
from widgets.constants import *

from googleapiclient.errors import HttpError

import validators
import data_filtering

from PIL import ImageFont
from configparser import ConfigParser



BASE_DIR = Path(__file__).parent.parent
ICONS = BASE_DIR / 'assets' / 'icons'
CERTIFICATES = BASE_DIR / 'certificates'
FONTS = BASE_DIR / 'fonts'
TEMPLATES = BASE_DIR / 'templates'
USERLISTS = BASE_DIR / 'userlists'
CONFIG = BASE_DIR / 'config.ini'


class FontSelector(ttk.Frame):
    def __init__(self, master: Misc, font: ttk.font.Font = None) -> None:
        super().__init__(master)
        self.font_dialog = FontDialog(parent=master.master, title='Font Selection')

        self.background_color = '#222222'

        # =-=-=-=-=-=-=-=- Load Icons -=-=-=-=-=--=-=-=-=-=-=
        image_files = {
            'userlists-folder-default': 'userlists_folder_default_32px.png',
            'userlists-folder-active': 'userlists_folder_active_32px.png',
            'fonts-folder-default': 'fonts_folder_default_32px.png',
            'fonts-folder-active': 'fonts_folder_active_32px.png',
            'templates-folder-default': 'templates_folder_default_32px.png',
            'templates-folder-active': 'templates_folder_active_32px.png'
        }

        self.photoimages = []
        for key, val in image_files.items():
            _path = ICONS / val
            self.photoimages.append(ttk.PhotoImage(name=key, file=_path))

        if font is None:
            font = ttk.font.Font(
                name='default_font',
                exists=False,
                family='Courier',
                size=48,
                weight=NORMAL,
                slant=ROMAN,
                underline=False,
                overstrike=False
            )
        self.font = font

        self.cco_labelframe = ttk.Labelframe(
            master=self,
            text='Certificate Creation Options',
            padding=10,
            width=330
        )
        self.cco_labelframe.pack(expand=YES, fill=BOTH)
        self.cco_labelframe.rowconfigure(5, weight=1)

        # =-=-=-=-=-=- Folders Dialogs -=-=-=-=-=--=-=

        self.folders_frame = ttk.Frame(self.cco_labelframe)
        self.folders_frame.grid(row=0, column=0, sticky=EW, pady=(0, 6))

        self.userlists_folder_button = ImageButton(
            master=self.folders_frame,
            default_image='userlists-folder-default',
            hover_image='userlists-folder-active',
            background=self.background_color,
        )
        self.userlists_folder_button.grid(row=0, column=0, padx=(0, 16))
        msg = 'Userlists folder.'
        ToolTip(self.userlists_folder_button, msg=msg, delay=1)

        self.fonts_folder_button = ImageButton(
            master=self.folders_frame,
            default_image='fonts-folder-default',
            hover_image='fonts-folder-active',
            background=self.background_color,
        )
        self.fonts_folder_button.grid(row=0, column=1, padx=(0, 16))
        msg = 'Fonts folder.'
        ToolTip(self.fonts_folder_button, msg=msg, delay=1)

        self.templates_folder_button = ImageButton(
            master=self.folders_frame,
            default_image='templates-folder-default',
            hover_image='templates-folder-active',
            background=self.background_color,
        )
        self.templates_folder_button.grid(row=0, column=2, padx=(0, 16))
        msg = 'Templates folder.'
        ToolTip(self.templates_folder_button, msg=msg, delay=1)

        # =-=-=-=-=-=- Colors Options -=-=-=-=-=--=-=

        self.color_Label = ttk.Label(
            master=self.cco_labelframe,
            text='Select Font Color',
            bootstyle=(INVERSE, SECONDARY),
            anchor=CENTER,
            font='-size 13'
        )
        self.color_Label.grid(row=1, column=0, sticky=EW, pady=6)

        self.color_selector = ColorSelector(master=self.cco_labelframe)
        self.color_selector.grid(row=2, column=0, sticky=EW)

        self.font_size_selector = FontSizeSelector(
            master=self.cco_labelframe,
            bootstyle=WARNING,
            maxfontsize=60
            )
        self.font_size_selector.grid(row=6, column=0, sticky=EW, pady=6)
        self.font_size_selector.amountusedvar.trace_add(
            'write', self._update_font_size)

        self.select_font_button = ttk.Button(
            master=self.cco_labelframe,
            bootstyle=(OUTLINE, WARNING),
            text='Select Font',
            padding=10,
            command=self._show_font_dialog
        )
        self.select_font_button.grid(row=7, column=0, sticky=EW, pady=6)

    def get_font_color(self) -> str:
        return self.color_selector.get_color_code()

    def get_font_size(self) -> int:
        return self.font_size_selector.amountusedvar.get()

    def _update_font_size(self, *args):
        new_size = self.font_size_selector.amountusedvar.get()
        self.font.configure(size=new_size)

    def _show_font_dialog(self):
        self.font_dialog.show()
        self.font = self.font_dialog._result
        self.font_size_selector.configure(amountused=self.font.cget('size'))


class FontSizeSelector(ttk.Meter):
    def __init__(
        self,
        master: Misc,
        fontsize=25,
        maxfontsize=50,
        *args,
        **kwargs
        ) -> None:
        super().__init__(
            master=master,
            amounttotal=maxfontsize,
            metersize=150,
            amountused=fontsize,
            stripethickness=8,
            subtext='Font Size',
            interactive=False,
            *args,
            **kwargs
        )

        # Get label child of meter widget
        meter_child = self.winfo_children()[0].winfo_children()[0]
        meter_child.bind('<Button-5>', self._wheelScroll) # Linux, wheel scroll down
        meter_child.bind('<Button-4>', self._wheelScroll)  # Linux, wheel scroll up
        meter_child.bind('<MouseWheel>', self._wheelScroll) # Windows wheel scroll keybind

    def get_font_size(self) -> int:
        return self.amountusedvar.get()

    def _increment_meter(self):
        new_value = self.amountusedvar.get() + 1
        # Make sure new value isn't out of bounds
        if new_value <= self.amounttotalvar.get():
            self.configure(amountused=new_value)

    def _decrement_meter(self):
        new_value = self.amountusedvar.get() - 1
        # Make sure new value isn't out of bounds
        if new_value >= 0:
            self.configure(amountused=new_value)

    def _wheelScroll(self, event: tk.Event):
        # Respond to Linux (event.num) or Windows (event.delta) wheel event
        if event.num == 4 or event.delta == 120: # Scroll up
            self._increment_meter()
        if event.num == 5 or event.delta == -120: # Scroll down
            self._decrement_meter()


class InfoInput(ttk.Labelframe):
    def __init__(
        self,
        master,
        testmode=True,
        logging=True
        ) -> None:
        super().__init__(master, text='Certificate Options', padding=(16, 10))

        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        self.font = '-size 13'
        self.background_color = '#222222'

        self.image_path = ttk.StringVar()
        self.info_file_path = ttk.StringVar()

        self.image_path.trace_add('write', self._invoke_image_handler)
        self.info_file_path.trace_add('write', self._invoke_info_file_handler)

        self.test_mode = ttk.BooleanVar(value=testmode)
        self.logging = ttk.BooleanVar(value=logging)

        # We manually call the handlers instead of tracing the vars because
        # we want to call the handlers whenever the complete path is given
        # and not when the path changes.

        # Ex. if a user types the path into the Entry the stringVar will
        # constantly change and the handler will be called multiple
        # times with an incompete path. To avoid this we will decide when
        # to call the handler
        self.image_changed_handler = None
        self.info_file_changed_handler = None

        # =-=-=-=-=-=-=-=- Load Icons -=-=-=-=-=--=-=-=-=-=-=
        image_files = {
            'template-default': 'template_default_32px.png',
            'template-active': 'template_active_32px.png',
            'userlist-default': 'userlist_default_32px.png',
            'userlist-active': 'userlist_active_32px.png'
        }

        self.photoimages = []
        for key, val in image_files.items():
            _path = ICONS / val
            self.photoimages.append(ttk.PhotoImage(name=key, file=_path))

        self.select_template_button = ImageButton(
            master=self,
            default_image='template-default',
            hover_image='template-active',
            background=self.background_color,
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
            hover_image='userlist-active',
            background=self.background_color,
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

        self.logging_mode_button = ttk.Checkbutton(
            master=self,
            bootstyle=(WARNING, TOGGLE, SQUARE),
            text=' Logging',
            variable=self.logging
        )
        self.logging_mode_button.grid(row=4, column=0, columnspan=2, sticky=W, pady=6)

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
            initialdir=TEMPLATES
        )

        if image_path not in {None, '', ()}:
            self.image_path.set(image_path)

    def _select_info_file(self):
        info_file_path = fd.askopenfilename(
            title='Select Info file',
            filetypes=(("Info files",".txt .exel .xlsx .csv"),("All files","*.*")),
            initialdir=USERLISTS
        )

        if info_file_path not in {None, '', ()}:
            self.info_file_path.set(info_file_path)

    def _invoke_image_handler(self, *args):
        if self.image_changed_handler is not None and self.image_path_entry.validate():
            self.image_changed_handler(self.image_path.get())

    def _invoke_info_file_handler(self, *args):
        if self.info_file_changed_handler is not None and self.info_path_entry.validate():
            self.info_file_changed_handler(self.info_file_path.get())


class EmailInput(ttk.Labelframe):
    def __init__(
        self,
        master,
        testemail='',
        realemail='',
        testmode=True,
        personalemail=False
        ) -> None:
        super().__init__(master, text='Emailing Options', padding=(16, 10))

        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        self.font = '-size 13'
        self.background_color = '#222222'

        self.test_email = ttk.StringVar()
        self.real_email = ttk.StringVar()

        self.test_mode = ttk.BooleanVar(value=testmode)
        self.personal_email = ttk.BooleanVar(value=personalemail)

        # =-=-=-=-=-=-=-=- Load Icons -=-=-=-=-=--=-=-=-=-=-=
        image_files = {
            'test_email-default': 'test_email_default_32px.png',
            'test_email-active': 'test_email_active_32px.png',
            'email-default': 'email_default_32px.png',
            'email-active': 'email_active_32px.png'
        }

        self.photoimages = []
        for key, val in image_files.items():
            _path = ICONS / val
            self.photoimages.append(ttk.PhotoImage(name=key, file=_path))

        self.test_email_button = ImageButton(
            master=self,
            default_image='test_email-default',
            hover_image='test_email-active',
            background=self.background_color
        )
        self.test_email_button.grid(row=0, column=0, padx=(0, 16), pady=4, sticky=W)
        msg = 'The email to use in test mode.'
        ToolTip(self.test_email_button, msg=msg, delay=1)

        self.test_email_entry = PlaceholderEntry(
            master=self,
            text=testemail,
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
            hover_image='email-active',
            background=self.background_color
        )
        self.real_email_button.grid(row=1, column=0, padx=(0, 16), pady=4, sticky=W)
        msg = 'The email to use when sending certificates.'
        ToolTip(self.real_email_button, msg=msg, delay=1)

        self.real_email_entry = PlaceholderEntry(
            master=self,
            text=realemail,
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
            text=' Use Test Email',
            variable=self.test_mode
        )
        self.test_mode_checkbutton.grid(row=3, column=0, columnspan=2, sticky=W, pady=6)

        self.personal_email_checkbutton = ttk.Checkbutton(
            master=self,
            bootstyle=(WARNING, TOGGLE, SQUARE),
            text=' Personal Email',
            variable=self.personal_email
        )
        self.personal_email_checkbutton.grid(row=4, column=0, columnspan=2, sticky=W, pady=6)

        self.send_emails_button = ttk.Button(
            master=self,
            bootstyle=(DANGER, OUTLINE),
            text='Send Emails',
            padding=9, width=18,
        )
        self.send_emails_button.grid(row=3, rowspan=2, column=2, sticky=E)


class MainWindow(object):
    def __init__(self, *args, **kwargs):
        self.root = ttk.Window(
            title='Certificates Creation',
            themename='darkly',
            minsize=(600, 565),
            *args,
            **kwargs
        )
        self.root.geometry('1600x800')

        self.app = App(self.root)
        self.app.pack(expand=YES, fill=BOTH, padx=10, pady=10)
        self.app.bind_class('TEntry', '<Return>', lambda _: self.app.focus_set(), add='+')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.app.save_config()
        self.app.clean_temp_files()


class App(ttk.Frame):
    def __init__(self, master) -> None:
        super().__init__(master)

        self.created_certificates = False

        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1, minsize=450)
        self.columnconfigure(1, weight=1)

        # =-=-=-=-=-=-=-=- Read Config -=-=-=-=-=--=-=-=-=-=-=

        config = ConfigParser()
        config.read(CONFIG)

        template_file = config.get('certificateCreation', 'defaultTemplate')
        userlist_file = config.get('certificateCreation', 'defaultUserlist')
        cc_test_mode = config.getboolean('certificateCreation', 'testMode')
        logging = config.getboolean('certificateCreation', 'logging')

        text_color = config.get('certificate', 'color')
        text_font  = config.get('certificate', 'font')
        self.text_font = text_font  # TODO
        text_font_size = config.getint('certificate', 'fontSize')

        text_alignment = config.get('certificateText', 'textAlignment')
        xcoord = config.getint('certificateText', 'xcoord')
        ycoord = config.getint('certificateText', 'ycoord')

        test_email = config.get('emailing', 'testEmail')
        real_email = config.get('emailing', 'realEmail')
        emailing_test_mode = config.getboolean('emailing', 'testMode')
        personal_email = config.getboolean('emailing', 'personalEmail')

        # =-=-=-=-=-=- Initialize Main Frames -=-=--=-=-=-=-=-=

        self.topframe = ttk.Frame(self)
        self.topframe.grid(row=0, column=0, columnspan=3, sticky=NSEW)

        self.lframe = ttk.Frame(self, padding=5)
        self.lframe.grid(row=2, column=0, sticky=NSEW)

        self.mframe = ttk.Frame(self, padding=5)
        self.mframe.grid(row=2, column=1, sticky=NSEW)

        self.rframe = ttk.Frame(self, padding=5)
        self.rframe.grid(row=2, column=2, sticky=NSEW)

        # =-=-=-=-=-=-=-=-=- Top Frame -=-=-=-=-=--=-=-=-=-=-=

        self.modes_selection_title = ttk.Label(
            master=self.topframe,
            text='Certificates Creator',
            font='-size 24 -weight bold'
        )
        self.modes_selection_title.pack(side=LEFT)

        self.mode = ttk.StringVar()
        self.modes_selection_label = ttk.Label(
            master=self.topframe,
            text='Select a mode:'
        )
        self.modes = ('Certificates Creator', 'Email Sender')
        self.modes_combobox= ttk.Combobox(
            master=self.topframe,
            bootstyle=(LIGHT),
            state=READONLY,
            textvariable=self.mode,
            width=20,
            values=self.modes
        )
        self.modes_combobox.current(0)
        self.modes_combobox.pack(padx=10, side=RIGHT)
        self.modes_selection_label.pack(side=RIGHT)

        self.mode.trace_add('write', self.switch_mode)

        self.progressbar_var = ttk.IntVar(value=0)
        self.progressbar = ttk.Progressbar(
            self,
            variable=self.progressbar_var,
            bootstyle=(DANGER)
        )

        self.seperator = ttk.Separator(self)
        self.seperator.grid(row=1, column=0, columnspan=3, sticky=EW, pady=6)

        # =-=-=-=-=-=-=-=-=- Left Frame -=-=-=-=-=--=-=-=-=-=-=

        self.lframe.rowconfigure(1, weight=1)
        self.lframe.columnconfigure(0, weight=1)

        self.certificate_options= InfoInput(
            master=self.lframe,
            testmode=cc_test_mode,
            logging=logging
        )
        self.certificate_options.grid(row=0, column=0, sticky=EW)
        self.certificate_options.create_certificates_button.configure(
            command=self.create_certificates)

        self.emailing_options = EmailInput(
            master=self.lframe,
            testemail=test_email,
            realemail=real_email,
            testmode=emailing_test_mode,
            personalemail=personal_email
            )
        self.emailing_options.send_emails_button.configure(
            command=self.send_emails
        )
        self.emailing_options.personal_email.trace_add(
            'write',
            lambda *_: self.email_creator.personal_email.set(
                self.emailing_options.personal_email.get()
            )
        )

        self.image_viewer = ImageViewer(
            master=self.lframe,
            text_alignment=text_alignment,
            xcoord=xcoord,
            ycoord=ycoord
            )
        self.image_viewer.grid(row=1, column=0, sticky=NSEW)

        self.certificate_options.image_changed_handler = self.load_image
        self.certificate_options.info_file_changed_handler = self.load_userlist

        # =-=-=-=-=-=-=-=- Middle Frame -=-=-=-=-=--=-=-=-=-=

        # Notebook with table and text tabs
        self.file_manager_notebook = ttk.Notebook(master=self.mframe, bootstyle=LIGHT)
        self.file_manager_notebook.pack(expand=YES, fill=BOTH, pady=(8, 0), padx=10)
        # enable key-binds for traversal
        self.file_manager_notebook.enable_traversal()

        # Initialize widgets
        self.text_editor = TextEditor(
            self.file_manager_notebook,
            scrollbar_bootstyle=(DEFAULT, ROUND)
        )
        self.data_viewer = DataViewer(
            self.file_manager_notebook,
            bootstyle=DARK,
            scrollbar_bootstyle=(DEFAULT, ROUND)
        )
        self.email_creator = EmailCreator(
            self.file_manager_notebook
        )
        self.logger = Logger(
            self.file_manager_notebook,
            scrollbar_bootstyle=(DEFAULT, ROUND)
        )

        self.filemanager_children = {}
        self.filemanager_children['Info File'] = self.text_editor
        self.filemanager_children['Name List'] = self.data_viewer
        self.filemanager_children['Email'] = self.email_creator
        self.filemanager_children['Logger'] = self.logger

        for key, value in self.filemanager_children.items():
            self.file_manager_notebook.add(value, text=key, sticky=NSEW)

        self.file_manager_notebook.bind('<<NotebookTabChanged>>', self.notebook_tab_changed)

        default_template_path = TEMPLATES / template_file
        default_userlist_path = USERLISTS / userlist_file

        self.certificate_options.image_path.set(default_template_path)
        self.certificate_options.info_file_path.set(default_userlist_path)

        # =-=-=-=-=-=-=-=-=- Right Frame -=-=-=-=-=--=-=-=-=-=-=

        self.font_configuration = FontSelector(master=self.rframe)
        self.font_configuration.color_selector.set_color(text_color)
        self.font_configuration.font_size_selector.amountusedvar.set(text_font_size)
        self.font_configuration.pack(expand=YES, fill=Y, side=RIGHT)

    def clean_temp_files(self):
        if os.path.exists('userlist.temp'):
            os.remove('userlist.temp')

    def save_config(self):
        config = ConfigParser()
        config.read(CONFIG)

        logging = str(self.certificate_options.logging.get()).lower()
        config.set('certificateCreation', 'logging', logging)

        text_color = self.font_configuration.get_font_color()[1:]
        config.set('certificate', 'color', text_color)
        text_font  = '' # TODO
        text_font_size = self.font_configuration.get_font_size()
        config.set('certificate', 'fontSize', str(text_font_size))

        coords = self.image_viewer.get_saved_coords()
        config.set('certificateText', 'xcoord', str(coords[0]))
        config.set('certificateText', 'ycoord', str(coords[1]))

        test_email = self.emailing_options.test_email.get()
        config.set('emailing', 'testEmail', test_email)
        real_email = self.emailing_options.real_email.get()
        config.set('emailing', 'realEmail', real_email)

        with open('config.ini', 'w') as configfile:
            config.write(configfile)

    def notebook_tab_changed(self, event: tk.Event):
        tab = event.widget.tab(CURRENT)['text']

        if tab == 'Info File':
            self.modes_combobox.current(0)
        elif tab == 'Email':
            self.modes_combobox.current(1)

    def load_userlist(self, path:str, *_):
        filetype = path.split('.')[-1]

        if filetype in {'exel', 'xls', 'xlsx', 'xlsm',
            'xlsb', 'odf', 'ods', 'odt'}:
            user_list = data_filtering.exel_to_list(path)
        elif filetype == 'csv':
            user_list = data_filtering.csv_to_list(path)
        else:
            user_list = data_filtering.txt_to_list(path)

        # List with valid users
        self.user_list = []
        # List with flagged users
        self.flagged_user_list = []

        # Filter users based on their flags
        for item in user_list:
            if item[2] == '':
                self.user_list.append(item)
            else:
                self.flagged_user_list.append(item)

        # Sort flaggedUserList based on flagIndex
        self.flagged_user_list = sorted(self.flagged_user_list, key=lambda a: a[2])
        # Clean dataViewer widgets
        self.filemanager_children['Name List']._reset()

        for item in self.user_list:
            self.filemanager_children['Name List'].insert_entry(
                values=[item[0], item[1]], save_edit=False)

        for item in self.flagged_user_list:
            tag = ''
            # Convert item flag to tree tag
            if item[2][0] == 'N':
                tag = 'flaggedName'
            elif item[2][0] == 'E':
                tag = 'flaggedEmail'

            self.filemanager_children['Name List'].insert_entry(
                values=[item[0], item[1]], tags=(tag), save_edit=False)

        data_filtering.list_to_txt(user_list)
        self.load_file(BASE_DIR / 'userlist.temp')
        # Switch to DataViewer tab
        self.file_manager_notebook.select(1)

    def load_file(self, path: str, *_):
        """ Load text file in the Text editor widget. """
        if os.path.exists(path):
            self.text_editor.load_file(path)

    def load_image(self, path: str, *_):
        """ Load image in the canvas widget. """
        # If the user closes the gui before selecting
        # a file, the path will be empty
        if os.path.exists(path):
            self.image_viewer.load_image(path)

    def switch_to_certificate_mode(self):
        self.emailing_options.grid_remove()
        self.certificate_options.grid(row=0, column=0, sticky=EW)

    def switch_to_emailing_mode(self):
        self.certificate_options.grid_remove()
        self.emailing_options.grid(row=0, column=0, sticky=EW)

    def switch_mode(self, *args):
        """ Change the app mode. If the current mode is emailing,
        switch to certificate creation and vise versa. """
        mode = self.modes_combobox.get()
        self.modes_selection_title.configure(text=mode)

        if self.mode.get() == 'Email Sender':
            self.switch_to_emailing_mode()
        else:
            self.switch_to_certificate_mode()

    def initialize_progressbar(self, maximum: int):
        """ Replace the seperator on the top frame with a
        progressbar with max value `maximum`. """
        self.seperator.grid_forget()
        self.progressbar.configure(maximum=maximum)
        self.progressbar_var.set(0)
        self.progressbar.grid(row=1, column=0, columnspan=3, sticky=EW, pady=6)

    def hide_progressbar(self):
        """ Hide the progressbar and replace it with a seperator. """
        self.progressbar.grid_forget()
        self.seperator.grid(row=1, column=0, columnspan=3, sticky=EW, pady=6)

    def create_certificates(self):
        font_path = FONTS / self.text_font
        font_path = FONTS / 'roboto-Regular.ttf'
        font_size = self.font_configuration.get_font_size()
        font = ImageFont.truetype(str(font_path), font_size)

        certificate_creator = CertificateCreator(
            image_path=self.certificate_options.image_path.get(),
            output_folder_path='certificates',
            font=font,
            font_color=self.font_configuration.get_font_color(),
            image_coords=self.image_viewer.get_saved_coords(),
            word_position=self.image_viewer.text_alignment_combobox.get(),
            compress_level=3,
            log_func = self.logger.log
        )

        if self.certificate_options.test_mode.get():
            entries_list = [('x', 'Name Surname', 'what@gmail.com')]
        else:
            entries_list = self.data_viewer.get_list_of_valid_entries()

        self.created_certificates = True
        self.initialize_progressbar(len(entries_list))

        lock = threading.Lock()
        App.launch_independent_tread(
            certificate_creator.create_certificates_from_list,
            lock,
            self.progressbar_var,
            entries_list,
            self.hide_progressbar
        )

    def send_emails(self):
        email_sender = EmailSender()

        sender = self.emailing_options.real_email_entry.get()
        email = self.email_creator.get_email()
        subject = email['subject']
        body = email['body']

        if self.emailing_options.test_mode.get():
            sender = self.emailing_options.test_email_entry.get()
        else:
            sender = self.emailing_options.real_email_entry.get()

        if self.emailing_options.personal_email.get():
            to = email['to']
            email_sender.send_email(
                sender,
                to,
                subject,
                msg_html=body
            )
            return

        if not self.created_certificates:
            Messagebox.show_warning(
                title='Certificate Emailing',
                message='Haven\'t Created Certificates!'
            )
            return

        def log(success: bool, index: str):
            entry = self.data_viewer.get_entry_from_index(index)
            if success:
                self.data_viewer._tree.item(entry, tags=['emailSuccess'])
            else:
                self.data_viewer._tree.item(entry, tags=['emailError'])

        userlist = self.data_viewer.get_list_of_valid_entries()
        self.initialize_progressbar(len(userlist))

        App.launch_independent_tread(
            EmailSenderWrapper.send_certificates,
            sender,
            subject,
            body,
            email_sender.create_message,
            email_sender.send_message,
            self.progressbar_var,
            log,
            self.hide_progressbar,
            userlist
        )

    @staticmethod
    def launch_independent_tread(
        target: Callable[..., Any],
        *args
    ):
        independent_thread = threading.Thread(
            target=target,
            args=args,
            daemon=True
        )
        independent_thread.start()


class EmailSenderWrapper:
    @staticmethod
    def send_certificates(
        sender: str,
        subject: str,
        body: str,
        create_message,
        send_message,
        progress_var: ttk.IntVar,
        log : Optional[Callable[[], Any]],
        cleanup_func : Optional[Callable[[], Any]],
        userlist: List[User]
    ) -> None:

        func = partial(
            EmailSenderWrapper.create_message,
            sender,
            subject,
            body,
            create_message
        )

        pool = mp.Pool(processes=5)
        message_list = pool.imap(
            func,
            userlist,
            chunksize=15
        )

        for message in message_list:
            try:
                send_message(message[1])
                log(True, int(message[0]))
            except HttpError as error:
                print('Couldn\'t send email, an http error has occured: ', error)
                log(False, int(message[0]))

            progress_var.set(progress_var.get() + 1)

        pool.close()
        pool.join()

        if cleanup_func:
            cleanup_func()

    @staticmethod
    def create_message(
        sender: str,
        subject: str,
        body: str,
        create_message,
        user: User
    ) -> Tuple[str, str]:
        certificate_path = CERTIFICATES / str(user[1].replace(' ', '_') + '.png')
        message = create_message(
            sender=sender,
            to=user[2],
            subject=subject,
            msg_html=body,
            attachments=[certificate_path]
        )
        return (user[0], message)


if __name__ == '__main__':
    with MainWindow() as w:
        w.root.mainloop()
