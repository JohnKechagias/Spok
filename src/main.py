import os
import threading
import multiprocessing as mp
from pathlib import Path
from functools import partial

import tkinter as tk
from tkinter.messagebox import askyesno
from tkinter.font import Font
from typing import Any, Callable

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs.dialogs import Messagebox

from folder_links import FolderLinks
from inputs import InfoInput, EmailInput

from services.certificate_creation import CertificateCreator
from services.email_sender import EmailSender
from widgets.font_selector import FontSelector

from widgets.logger import Logger
from widgets.canvas_image import ImageViewer
from widgets.email_creator import EmailCreator
from widgets.user_viewer import UserViewer
from widgets.constants import *

from googleapiclient.errors import HttpError

from services.data_filtering import file_to_ulist

from PIL import ImageFont
from configparser import ConfigParser
import services.assets_manager as assets_manager



BASE_DIR = Path(__file__).parent.parent
ASSETS = BASE_DIR / 'assets'
CERTIFICATES = BASE_DIR / 'certificates'
FONTS = BASE_DIR / 'fonts'
TEMPLATES = BASE_DIR / 'templates'
USERLISTS = BASE_DIR / 'userlists'
CONFIG = BASE_DIR / 'config.ini'


class MainWindow(object):
    def __init__(self, *args, **kwargs):
        self.root = ttk.Window(
            title='Certificates Creation',
            themename=THEMENAME,
            iconphoto=(ASSETS / 'icons' / 'icon.png'),
            minsize=(1200, 565),
            *args,
            **kwargs
        )
        self.root.geometry('1600x800')

        self.app = App(self.root)
        self.app.pack(expand=YES, fill=BOTH, padx=10, pady=10)

        self.app.bind_class('TEntry',
            '<Return>',
            lambda _: self.app.focus_set(),
            add='+'
        )

        self.app.bind_class('TEntry',
            '<Escape>',
            lambda _: self.app.focus_set(),
            add='+'
        )

        self.root.protocol(
            'WM_DELETE_WINDOW',
            lambda: self.app.save_state(self.root.destroy)
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class App(ttk.Frame):
    def __init__(self, master) -> None:
        super().__init__(master)

        self.created_certificates = False

        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1, minsize=450)
        self.columnconfigure(1, weight=1)

        # =-=-=-=-=-=-=-=- Load Icons -=-=-=-=-=--=-=-=-=-=-=

        assets_manager.load_assets(ASSETS)

        # =-=-=-=-=-=-=-=- Read Config -=-=-=-=-=--=-=-=-=-=-=

        config = ConfigParser()
        config.read(CONFIG, encoding='UTF-8')

        template_file = config.get('certificateCreation', 'template')
        userlist_file = config.get('certificateCreation', 'userlist')

        font_color = config.get('font', 'color')
        font_family = config.get('font', 'family')
        font_size = config.getint('font', 'size')
        font_weight = config.get('font', 'weight')
        font_slant = config.get('font', 'slant')

        font = Font(
            name='config_font',
            exists=False,
            family=font_family,
            size=font_size,
            weight=font_weight,
            slant=font_slant,
            underline=False,
            overstrike=False
        )

        text_alignment = config.get('certificateText', 'alignment')
        xcoord = config.getint('certificateText', 'xcoord')
        ycoord = config.getint('certificateText', 'ycoord')

        test_email = config.get('emailing', 'testEmail')
        real_email = config.get('emailing', 'realEmail')
        email_subject = config.get('emailing', 'subject')
        email_body = config.get('emailing', 'body')

        # =-=-=-=-=-=- Initialize Main Frames -=-=--=-=-=-=-=-=

        self.topframe = ttk.Frame(self)
        self.topframe.grid(row=0, column=0, columnspan=3, sticky=NSEW)
        self.topframe.columnconfigure(2, weight=1)

        self.lframe = ttk.Frame(self, padding=5)
        self.lframe.grid(row=2, column=0, sticky=NSEW)

        self.mframe = ttk.Frame(self, padding=5)
        self.mframe.grid(row=2, column=1, sticky=NSEW)

        self.rframe = ttk.Frame(self, padding=5)
        self.rframe.grid(row=2, column=2, sticky=NSEW)

        # =-=-=-=-=-=-=-=-=- Top Frame -=-=-=-=-=--=-=-=-=-=-=

        self.main_title = ttk.Label(
            self.topframe,
            text='Vicer',
            font='-size 24 -weight bold'
        )
        self.main_title.grid(row=0, column=0)

        self.secondary_title = ttk.Label(
            self.topframe,
            text='a certificate creator',
            font='-size 16'
        )
        self.secondary_title.grid(row=0, column=1, padx=5, pady=(9, 0))

        folders = [USERLISTS, FONTS, TEMPLATES, CERTIFICATES]
        self.folder_links = FolderLinks(
            self.topframe,
            folders
        )
        self.folder_links.grid(row=0, column=2, sticky=E)

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
            templates_path=TEMPLATES,
            userlists_path=USERLISTS,
            testmode=True
        )
        self.certificate_options.grid(row=0, column=0, sticky=EW)
        self.certificate_options.create_certificates_button.configure(
            command=self.create_certificates
        )

        self.certificate_options.image_changed_handler = self.load_image
        self.certificate_options.info_file_changed_handler = self.load_userlist

        self.emailing_options = EmailInput(
            master=self.lframe,
            testemail=test_email,
            realemail=real_email,
            testmode=True
        )
        self.emailing_options.send_emails_button.configure(
            command=self.send_emails
        )

        self.image_viewer = ImageViewer(
            master=self.lframe,
            text_alignment=text_alignment,
            xcoord=xcoord,
            ycoord=ycoord
        )
        self.image_viewer.grid(row=1, column=0, sticky=NSEW)

        # =-=-=-=-=-=-=-=- Middle Frame -=-=-=-=-=--=-=-=-=-=

        # Notebook with table and text tabs
        self.file_manager_notebook = ttk.Notebook(master=self.mframe, bootstyle=LIGHT)
        self.file_manager_notebook.pack(expand=YES, fill=BOTH, pady=(8, 0), padx=10)
        # enable key-binds for traversal
        self.file_manager_notebook.enable_traversal()

        # Initialize widgets
        self.data_viewer = UserViewer(
            self.file_manager_notebook,
            bootstyle=DARK,
            scrollbar_bootstyle=(DEFAULT, ROUND)
        )

        self.email_creator = EmailCreator(
            self.file_manager_notebook,
            subject=email_subject,
            body=email_body
        )

        self.logger = Logger(
            self.file_manager_notebook,
            scrollbar_bootstyle=(DEFAULT, ROUND)
        )

        self.filemanager_children = {}
        self.filemanager_children['Name List'] = self.data_viewer
        self.filemanager_children['Email'] = self.email_creator
        self.filemanager_children['Logger'] = self.logger

        for key, value in self.filemanager_children.items():
            self.file_manager_notebook.add(value, text=key, sticky=NSEW)

        self.file_manager_notebook.bind(
            '<<NotebookTabChanged>>',
            self.notebook_tab_changed
        )

        default_template_path = TEMPLATES / template_file
        default_userlist_path = USERLISTS / userlist_file

        self.certificate_options.image_path.set(default_template_path)
        self.certificate_options.info_file_path.set(default_userlist_path)

        # =-=-=-=-=-=-=-=-=- Right Frame -=-=-=-=-=--=-=-=-=-=-=

        font_families = [i.stem.replace('-', ' ') for i in FONTS.iterdir() if i.suffix == '.ttf']
        self.font_configuration = FontSelector(
            self.rframe,
            font_families,
            font,
            color=font_color
        )
        self.font_configuration.pack(side=TOP, expand=TRUE, fill=BOTH)

    def save_state(self, callback, *args, **kwargs):
        try:
            self.clean_temp_files()
            self.save_config()
        except:
            pass
        finally:
            callback(*args, **kwargs)

    def clean_temp_files(self):
        if os.path.exists('userlist.temp'):
            os.remove('userlist.temp')

    def save_config(self):
        config = ConfigParser()
        config.read(CONFIG, encoding='UTF-8')

        font = self.font_configuration.font
        color = self.font_configuration.color[1:]

        config.set('font', 'color', color)
        config.set('font', 'family', font.cget('family'))
        config.set('font', 'size', str(font.cget('size')))
        config.set('font', 'weight', font.cget('weight'))
        config.set('font', 'slant', font.cget('slant'))

        alignment = self.image_viewer.text_alignment.get()
        coords = self.image_viewer.get_saved_coords()

        config.set('certificateText', 'alignment', alignment)
        config.set('certificateText', 'xcoord', str(coords[0]))
        config.set('certificateText', 'ycoord', str(coords[1]))

        test_email = self.emailing_options.test_email.get()
        real_email = self.emailing_options.real_email.get()
        if (email_subject := self.email_creator.get_subject()) == 'Subject':
            email_subject = 'Example subject'
        if not len(email_body := self.email_creator.get_body().rstrip()):
            email_body = 'Example body'

        config.set('emailing', 'testEmail', test_email)
        config.set('emailing', 'realEmail', real_email)
        config.set('emailing', 'subject', email_subject)
        config.set('emailing', 'body', email_body)

        with open(CONFIG, 'w', encoding='UTF-8') as configfile:
            config.write(configfile)

    def notebook_tab_changed(self, event: tk.Event):
        match event.widget.tab(CURRENT)['text']:
            case 'Name List':
                self.switch_to_certificate_mode()
            case 'Email':
                self.switch_to_emailing_mode()

    def load_userlist(self, path: str, *_):
        try:
            userlist = file_to_ulist(Path(path))
            self.data_viewer.load_list(userlist)
            # Switch to DataViewer tab
            self.file_manager_notebook.select(0)
        except NotImplementedError:
            pass

    def load_image(self, path: str, *_):
        """ Load image in the canvas widget. """
        # If the user closes the gui before selecting
        # a file, the path will be empty
        if os.path.exists(path):
            self.image_viewer.load_image(path)

    def switch_to_emailing_mode(self):
        self.certificate_options.grid_remove()
        self.emailing_options.grid(row=0, column=0, sticky=EW)

    def switch_to_certificate_mode(self):
        self.emailing_options.grid_remove()
        self.certificate_options.grid(row=0, column=0, sticky=EW)

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
        font = self.font_configuration.font
        font_path = FONTS / f'{font.cget("family").replace(" ", "-")}.ttf'
        image_font = ImageFont.truetype(str(font_path), font.cget('size'))

        certificate_creator = CertificateCreator(
            image_path=self.certificate_options.image_path.get(),
            output_folder=CERTIFICATES,
            font=image_font,
            font_color=self.font_configuration.color,
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
        answer = askyesno('Emailing', 'You are about to send emails. Continue?')

        if not answer:
            return

        email_sender = EmailSender()

        sender = self.emailing_options.real_email_entry.get()
        email = self.email_creator.get_email()
        subject = email['subject']
        body = email['body']

        if self.emailing_options.test_mode.get():
            sender = self.emailing_options.test_email_entry.get()
        else:
            sender = self.emailing_options.real_email_entry.get()

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

        if self.emailing_options.test_mode.get():
            userlist = []
            for item in self.data_viewer.get_num_of_valid_entries(10):
                item = list(item)
                item[2] = self.emailing_options.test_email.get()
                userlist.append(tuple(item))
        else:
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
        log : Callable[[], Any] | None,
        cleanup_func : Callable[[], Any] | None,
        userlist: list[User]
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
    ) -> tuple[str, str]:
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
    # Prevents new processes from duplicating the main window
    mp.freeze_support()

    with MainWindow() as w:
        w.root.mainloop()
