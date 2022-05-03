import os

import tkinter as tk
from tkinter import filedialog as fd

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs.dialogs import FontDialog
from certificateCreation import CertificateCreator

from widgets.logger import Logger
from widgets.canvas_image import ImageViewer
from widgets.color_selector import ColorSelector
from widgets.data_viewer import DataViewer
from widgets.email_creator import EmailCreator
from widgets.placeholder_entry import PlaceholderEntry
from widgets.text_editor import TextEditor
from widgets.constants import *

import validators
import dataFiltering



class FontSelector(ttk.Frame):
    def __init__(self, master, font:ttk.font.Font=None):
        super().__init__(master)
        self.font_dialog = FontDialog(parent=master.master, title='Font Selection')
        self.show_button = ttk.Button(self, bootstyle=(DARK))
        self.font = font

        self.cco_labelframe = ttk.Labelframe(
            master=self,
            text='Certificate Creation Options',
            padding=10,
            width=330
        )
        self.cco_labelframe.pack(expand=YES, fill=BOTH)

        self.cco_labelframe.rowconfigure(5, weight=1)

        self.select_font_button = ttk.Button(
            master=self.cco_labelframe,
            bootstyle=(OUTLINE, WARNING),
            text='Select Font',
            padding=10,
            command=self._showFontDialog
        )
        self.select_font_button.grid(row=0, column=0, sticky=EW, pady=6)

        # =-=-=-=-=-=- Colors Options -=-=-=-=-=--=-=

        self.color_Label = ttk.Label(
            master=self.cco_labelframe,
            text='Select Font Color',
            bootstyle=(INVERSE, SECONDARY),
            anchor=CENTER,
            font="-size 13"
        )
        self.color_Label.grid(row=1, column=0, sticky=EW, pady=(6, 10))

        self.color_selector = ColorSelector(master=self.cco_labelframe)
        self.color_selector.grid(row=2, column=0, sticky=EW)

        self.font_size_selector = FontSizeSelector(master=self.cco_labelframe, bootstyle=WARNING)
        self.font_size_selector.grid(row=3, column=0, sticky=EW)

        self.font_size_selector.meter.amountusedvar.trace_add(
            'write', self._update_font_size)

        self.select_font_button = ttk.Button(
            master=self.cco_labelframe,
            bootstyle=(OUTLINE, WARNING),
            text='Close',
            padding=9
        )
        self.select_font_button.grid(row=6, column=0, sticky=EW, pady=6)

    def _update_font_size(self, *args):
        new_size = self.font_size_selector.meter.amountusedvar.get()
        self.font.configure(size=new_size)

    def _showFontDialog(self):
        self.font_dialog.show()
        self.font = self.font_dialog._result
        self.font_size_selector.meter.configure(amountused=self.font.cget('size'))

    def _hideWidget(self):
        self.cco_labelframe.pack_forget()
        self.show_button.pack(expand=YES, fill=BOTH)

    def _showWidget(self):
        self.show_button.pack_forget()
        self.cco_labelframe.pack(expand=YES, fill=Y, anchor=NE, side=RIGHT)


class FontSizeSelector(ttk.Frame):
    def __init__(self, master, fontsize=18, maxfontsize=50, *args, **kwargs):
        super().__init__(master)

        self.meter = ttk.Meter(
            master=self,
            amounttotal=maxfontsize,
            metersize=150,
            amountused=fontsize,
            stripethickness=8,
            subtext="Font Size",
            interactive=False,
            *args,
            **kwargs
        )
        self.meter.pack(side=TOP, padx=6, pady=6)

        # get label child of meter widget
        meter_child = self.meter.winfo_children()[0].winfo_children()[0]
        meter_child.bind('<Button-5>', self._wheelScroll) # Linux, wheel scroll down
        meter_child.bind('<Button-4>', self._wheelScroll)  # Linux, wheel scroll up
        meter_child.bind('<MouseWheel>', self._wheelScroll) # windows wheel scroll keybind

    def _increment_meter(self):
        new_value = self.meter.amountusedvar.get() + 1
        # make sure new value isn't out of bounds
        if new_value <= self.meter.amounttotalvar.get():
            self.meter.configure(amountused=new_value)

    def _decrement_meter(self):
        new_value = self.meter.amountusedvar.get() - 1
        # make sure new value isn't out of bounds
        if new_value >= 0:
            self.meter.configure(amountused=new_value)

    def _wheelScroll(self, event:tk.Event):
        # Respond to Linux (event.num) or Windows (event.delta) wheel event
        if event.num == 4 or event.delta == 120: # scroll up
            self._increment_meter()
        if event.num == 5 or event.delta == -120: # scroll down
            self._decrement_meter()

    def getFontSize(self) -> int:
        return self.meter.amountusedvar.get()


class InfoInput(ttk.Labelframe):
    def __init__(
        self,
        master,
        test_mode=True,
        logging=True
        ):
        super().__init__(master, text='Certificate Options', padding=(16, 10))

        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        self.font = '-size 13'

        self.image_path = ttk.StringVar()
        self.info_file_path = ttk.StringVar()

        self.image_path.trace_add('write', self._invoke_image_handler)
        self.info_file_path.trace_add('write', self._invoke_info_file_handler)

        self.test_mode = ttk.BooleanVar(value=test_mode)
        self.logging = ttk.BooleanVar(value=logging)

        # We manually call the hanlders instead of tracing the vars because
        # we want to call the handlers whenever the complete path is given
        # and not when the path changes.

        # Ex. if a user types the path into the Entry the stringVar will
        # constantly change and the handler will be called multiple
        # times with an incompete path. To avoid this we will decide when
        # to call the handler
        self.image_changed_handler = None
        self.info_file_changed_handler = None

        self.select_template_button = ttk.Button(
            master=self,
            bootstyle=(DEFAULT),
            text='Select Template Image',
            padding=8,
            width=19,
            command=self._select_image_file
        )
        self.select_template_button.grid(row=0, column=0, padx=(0, 8), pady=4)

        self.image_path_entry = ttk.Entry(
            master=self,
            font=self.font,
            textvariable=self.image_path)
        self.image_path_entry.grid(row=0, column=1, columnspan=2, pady=6, sticky=EW)

        self.image_path_entry.bind('<Return>', lambda _: self._invoke_image_handler(), add='+')

        validators.add_file_type_validation(self.image_path_entry,
            filetypes={'img', 'png', 'jpeg', 'jpg'})

        self.select_info_file_button = ttk.Button(
            master=self,
            bootstyle=(DEFAULT),
            text='Select Info File',
            padding=8,
            width=19,
            command=self._select_info_file
        )
        self.select_info_file_button.grid(row=1, column=0, padx=(0, 8), pady=4)

        self.info_path_entry = ttk.Entry(master=self, font=self.font, textvariable=self.info_file_path)
        self.info_path_entry.grid(row=1, column=1, columnspan=2, pady=6, sticky=EW)

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
        self.error_checking_mode_checkbutton.grid(row=3, column=0, sticky=W, pady=6)

        self.clean_mode_button = ttk.Checkbutton(
            master=self,
            bootstyle=(WARNING, TOGGLE, SQUARE),
            text=' Logging',
            variable=self.logging
        )
        self.clean_mode_button.grid(row=4, column=0, sticky=W, pady=6)

        self.create_certificates_button = ttk.Button(
            master=self,
            bootstyle=(DANGER, OUTLINE),
            text='Create Certificates',
            padding=9, width=18,
        )
        self.create_certificates_button.grid(row=3, rowspan=2, column=2, sticky=E)

    def _select_image_file(self):
        self._selectFile(self.image_path, ("Image files",".img .png .jpeg .jpg"))

    def _select_info_file(self):
        self._selectFile(self.info_file_path, ("Info files",".txt .exel .xlsx .csv"))

    def _invoke_image_handler(self, *args):
        if self.image_changed_handler is not None and self.image_path_entry.validate():
            self.image_changed_handler(self.image_path.get())

    def _invoke_info_file_handler(self, *args):
        if self.info_file_changed_handler is not None and self.info_path_entry.validate():
            self.info_file_changed_handler(self.info_file_path.get())

    def _selectFile(self, stringVar:tk.StringVar, filetype):
        stringVar.set(fd.askopenfilename(filetypes=(filetype,("All files","*.*"))))


class EmailInput(ttk.Labelframe):
    def __init__(
        self,
        master,
        testmode=True,
        twolevelauth=True
        ):
        super().__init__(master, text='Emailing Options', padding=(16, 10))

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.font = '-size 13'

        self.test_email = ttk.StringVar()
        self.real_email = ttk.StringVar()

        self.test_mode = ttk.BooleanVar(value=testmode)
        self.two_level_auth = ttk.BooleanVar(value=twolevelauth)

        self.test_email_entry = PlaceholderEntry(
            master=self,
            placeholder='Testing Email',
            font=self.font,
            textvariable=self.test_email
        )
        self.test_email_entry.grid(row=0, column=0, columnspan=2, pady=6, sticky=EW)

        self.test_email_entry.bind('<Return>',
            lambda _: self.test_email_entry.validate(), add='+')
        validators.add_email_validation(self.test_email_entry)

        self.real_email_entry = PlaceholderEntry(
            master=self,
            placeholder='Real Email',
            font=self.font,
            textvariable=self.real_email
        )
        self.real_email_entry.grid(row=1, column=0, columnspan=2, pady=6, sticky=EW)

        self.real_email_entry.bind('<Return>',
            lambda _: self.real_email_entry.validate(), add='+')
        validators.add_email_validation(self.real_email_entry)

        ttk.Separator(self).grid(row=2, column=0, columnspan=2, pady=10, sticky=EW)

        self.test_mode_checkbutton = ttk.Checkbutton(
            master=self,
            bootstyle=(DANGER, TOGGLE, SQUARE),
            text=' Use Test Email',
            variable=self.test_mode
        )
        self.test_mode_checkbutton.grid(row=3, column=0, sticky=W, pady=6)

        self.two_level_auth_checkbutton = ttk.Checkbutton(
            master=self,
            bootstyle=(WARNING, TOGGLE, SQUARE),
            text=' Two level Auth',
            variable=self.two_level_auth
        )
        self.two_level_auth_checkbutton.grid(row=4, column=0, sticky=W, pady=6)

        self.send_emails_button = ttk.Button(
            master=self,
            bootstyle=(DANGER, OUTLINE),
            text='Send Emails',
            padding=9, width=18,
        )
        self.send_emails_button.grid(row=3, rowspan=2, column=1, sticky=E)



class App(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.rowconfigure(2, weight=1)

        self.columnconfigure(0, weight=1, minsize=450)
        self.columnconfigure(1, weight=1)

        # =-=-=-=-=-=-=-=-=- Top Frame -=-=-=-=-=--=-=-=-=-=-=

        self.topframe = ttk.Frame(self)
        self.topframe.grid(row=0, column=0, columnspan=3, sticky=NSEW)

        self.modes_selection_title = ttk.Label(
            master=self.topframe, text="Certificates Creator", font="-size 24 -weight bold"
        )
        self.modes_selection_title.pack(side=LEFT)

        self.mode = ttk.StringVar()
        self.modes_selection_label = ttk.Label(master=self.topframe, text="Select a mode:")
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

        def change_mode(e):
            mode = self.modes_combobox.get()
            self.modes_selection_title.configure(text=mode)

        self.modes_combobox.bind("<<ComboboxSelected>>", change_mode, add='+')
        self.mode.trace_add('write', self.change_mode)

        ttk.Separator(self).grid(row=1, column=0, columnspan=3, sticky=EW, pady=6)

        self.lframe = ttk.Frame(self, padding=5)
        self.lframe.grid(row=2, column=0, sticky=NSEW)

        self.mframe = ttk.Frame(self, padding=5)
        self.mframe.grid(row=2, column=1, sticky=NSEW)

        self.rframe = ttk.Frame(self, padding=5)
        self.rframe.grid(row=2, column=2, sticky=NSEW)

        # =-=-=-=-=-=-=-=-=- Left Frame -=-=-=-=-=--=-=-=-=-=-=

        self.lframe.rowconfigure(1, weight=1)
        self.lframe.columnconfigure(0, weight=1)

        self.certificate_options= InfoInput(master=self.lframe)
        self.certificate_options.grid(row=0, column=0, sticky=EW)
        self.certificate_options.create_certificates_button.configure(
            command=self.create_certificates)

        self.emailing_options = EmailInput(master=self.lframe)

        self.image_viewer = ImageViewer(self.lframe)
        self.image_viewer.grid(row=1, column=0, sticky=NSEW)

        self.certificate_options.image_changed_handler = self.load_image
        self.certificate_options.info_file_changed_handler = self.load_info_file

        # =-=-=-=-=-=-=-=-=- File Manager -=-=-=-=-=--=-=-=-=-=

        # notebook with table and text tabs
        self.file_manager_notebook = ttk.Notebook(master=self.mframe, bootstyle=LIGHT)
        self.file_manager_notebook.pack(expand=YES, fill=BOTH, pady=(8, 0), padx=10)
        # enable key-binds for traversal
        self.file_manager_notebook.enable_traversal()

        # initialize widgets
        self.text_editor = TextEditor(self.file_manager_notebook)
        self.data_viewer = DataViewer(self.file_manager_notebook, bootstyle=DARK)
        self.email_creator = EmailCreator(self.file_manager_notebook)
        self.logger = Logger(self.file_manager_notebook)

        self.filemanager_children = {}
        self.filemanager_children['Info File'] = self.text_editor
        self.filemanager_children['Name List'] = self.data_viewer
        self.filemanager_children['Email'] = self.email_creator
        self.filemanager_children['Logger'] = self.logger

        for key, value in self.filemanager_children.items():
            self.file_manager_notebook.add(value, text=key, sticky=NSEW)

        self.certificate_options.info_file_path.set(
            f'{os.curdir}/assets/text.txt')
        self.certificate_options.image_path.set(
            f'{os.curdir}/assets/template.png')

        # =-=-=-=-=-=- Certificate Creation Options -=-=-=-=-=--=-=

        self.font_configuration = FontSelector(master=self.rframe)
        self.font_configuration.pack(expand=YES, fill=Y, side=RIGHT)

    def load_info_file(self, path:str, *_) -> None:
        logging = self.certificate_options.logging.get()
        filetype = path.split('.')[-1]

        if filetype in {'exel', 'xlsx'}:
            user_list = dataFiltering.exel_to_list(path)
        elif filetype == 'csv':
            user_list = dataFiltering.csv_to_list(path)
        else:
            user_list = dataFiltering.txt_to_list(path)

        # list with valid users
        self.user_list = []
        # list with flagged users
        self.flagged_user_list = []

        # filter users based on their flags
        for item in user_list:
            if item[2] == '':
                self.user_list.append(item)
            else:
                self.flagged_user_list.append(item)

        # sort flaggedUserList based on flagIndex
        self.flagged_user_list = sorted(self.flagged_user_list, key=lambda a: a[2])

        # clean dataViewer widgets
        self.filemanager_children['Name List']._reset()

        for item in self.user_list:
            self.filemanager_children['Name List'].insert_entry(
                values=[item[0], item[1]], save_edit=False)

        for item in self.flagged_user_list:
            tag = ''
            # convert item flag to tree tag
            if item[2][0] == 'N':
                tag = 'flaggedName'
            elif item[2][0] == 'E':
                tag = 'flaggedEmail'

            self.filemanager_children['Name List'].insert_entry(
                values=[item[0], item[1]], tags=(tag), save_edit=False)

        #dataFiltering.listToTxt(userList)
        self.load_file('cleanFile.txt')

        # switch to DataViewer tab
        self.file_manager_notebook.select(1)

    def load_file(self, path:str, *_):
        """Load text file in the Text editor widget"""
        if os.path.exists(path):
            self.filemanager_children['Info File'].load_file(path)

    def load_image(self, path:str, *_):
        """Load image in the canvas widget"""
        # if the user closes the gui before selecting
        # a file, the path will be empty
        if os.path.exists(path):
            self.image_viewer.load_image(path)

    def changeToCertificateMode(self):
        self.emailing_options.grid_remove()
        self.certificate_options.grid(row=0, column=0, sticky=EW)

    def changeToEmailingMode(self):
        self.certificate_options.grid_remove()
        self.emailing_options.grid(row=0, column=0, sticky=EW)

    def change_mode(self, *args):
        if self.mode.get() == 'Email Sender':
            self.changeToEmailingMode()
        else:
            self.changeToCertificateMode()

    def create_certificates(self):
        certificate_creator = CertificateCreator(
            image_path = self.certificate_options.image_path.get(),
            output_folder_path = 'certificates',
            font = self.font_configuration.font,
            font_color = tuple(self.font_configuration.color_selector.get_color_tuple()),
            image_coords = self.image_viewer.get_saved_coords(),
            word_position = LEFT,
            log_func = self.logger.log
        )

        if self.certificate_options.test_mode.get():
            entries_list = (('x', 'John Kechagias', 'what@gmail.com'))
        else:
            entries_list = self.filemanager_children['Name List'].get_list_of_entries()

        certificate_creator.create_certificates_from_list(entries_list)


if __name__ == "__main__":
    window = ttk.Window("Certificates Creation", themename="darkly", minsize=(600, 565))
    window.geometry('1600x800')

    app = App(window)
    app.pack(expand=YES, fill=BOTH, padx=10, pady=10)

    app.bind('<Configure>', lambda e: print(e.height))
    window.mainloop()