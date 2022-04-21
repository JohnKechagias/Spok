import os

import tkinter as tk
from tkinter import filedialog as fd

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs.dialogs import FontDialog
from widgets import *

import validators
import dataFiltering

class FontChooser(ttk.Frame):
    def __init__(self, master, defaultFontSize=18, maxFontSize=50, *args, **kwargs):
        super().__init__(master)
        
        self.meter = ttk.Meter(
            master=self,
            amounttotal=maxFontSize,
            metersize=150,
            amountused=defaultFontSize,
            stripethickness=8,
            subtext="Font Size",
            interactive=False,
            *args,
            **kwargs
        )
        self.meter.pack(side=TOP, padx=6, pady=6)

        # get label child of meter widget
        meterChild = self.meter.winfo_children()[0].winfo_children()[0]
        meterChild.bind('<Button-5>', self._wheelScroll) # Linux, wheel scroll down
        meterChild.bind('<Button-4>', self._wheelScroll)  # Linux, wheel scroll up
        meterChild.bind('<MouseWheel>', self._wheelScroll) # windows wheel scroll keybind

    def _incrementMeter(self):
        newValue = self.meter.amountusedvar.get() + 1
        # make sure new value isn't out of bounds
        if newValue <= self.meter.amounttotalvar.get():
            self.meter.configure(amountused=newValue)
        
    def _decrementMeter(self):
        newValue = self.meter.amountusedvar.get() - 1
        # make sure new value isn't out of bounds
        if newValue >= 0:
            self.meter.configure(amountused=newValue)

    def _wheelScroll(self, event:tk.Event):
        # Respond to Linux (event.num) or Windows (event.delta) wheel event
        if event.num == 4 or event.delta == 120: # scroll up
            self._incrementMeter()
        if event.num == 5 or event.delta == -120: # scroll down
            self._decrementMeter()

    def getFontSize(self) -> int:
        return self.meter.amountusedvar.get()

class InfoInput(ttk.Labelframe):
    def __init__(
        self, 
        master,
        enableErrorChecking=True,
        enableLogging=True
        ):
        super().__init__(master, text='Certificate Options', padding=(16, 10))

        self.columnconfigure(1, weight=1)        
        self.columnconfigure(2, weight=1)

        self.font = '-size 13'
        self.infoFileType = ''
        
        self._imagePath = ttk.StringVar()
        self._infoFilePath = ttk.StringVar()

        self.enableErrorChecking = ttk.BooleanVar(value=enableErrorChecking)
        self.enableLogging = ttk.BooleanVar(value=enableLogging)

        # We manually call the hanlders instead of tracing the vars because
        # we want to call the handlers whenever the complete path is given
        # and not when the path changes.

        # Ex. if a user types the path into the Entry the stringVar will
        # constantly change and the handler will be called multiple
        # times with an incompete path. To avoid this we will decide when
        # to call the handler
        self.imageFunctionToCall = None
        self.infoFileFunctionToCall = None

        self.selectTemplateButton = ttk.Button(
            master=self,
            bootstyle=(DEFAULT),
            text='Select Template Image',
            padding=8, 
            width=19,
            command=self._selectImageFile
        )
        self.selectTemplateButton.grid(row=0, column=0, padx=(0, 8), pady=4)

        self.imagePathEntry = ttk.Entry(
            master=self,
            font=self.font,
            textvariable=self._imagePath)
        self.imagePathEntry.grid(row=0, column=1, columnspan=2, pady=6, sticky=EW)

        self.imagePathEntry.bind('<Return>', lambda _: self._callImagePathHandler(), add='+')

        validators.addFileTypeValidation(self.imagePathEntry, 
            filetypes={'img', 'png', 'jpeg', 'jpg'})

        self.selectInfoFileButton = ttk.Button(
            master=self,
            bootstyle=(DEFAULT),
            text='Select Info File',
            padding=8, 
            width=19,
            command=self._selectInfoFile
        )
        self.selectInfoFileButton.grid(row=1, column=0, padx=(0, 8), pady=4)

        self.infoPathEntry = ttk.Entry(master=self, font=self.font, textvariable=self._infoFilePath)
        self.infoPathEntry.grid(row=1, column=1, columnspan=2, pady=6, sticky=EW)

        self.infoPathEntry.bind('<Return>', lambda _: self._callInfoFilePathHandler(), add='+')

        validators.addFileTypeValidation(self.infoPathEntry,
            filetypes={'txt', 'exel', 'xlsx'})

        ttk.Separator(self).grid(row=2, column=0, columnspan=3, pady=10, sticky=EW)

        self.errorCheckModeCheckButton = ttk.Checkbutton(
            master=self,
            bootstyle=(WARNING, TOGGLE, SQUARE),
            text=' Error Checking',
            variable=self.enableErrorChecking
        )
        self.errorCheckModeCheckButton.grid(row=3, column=0, sticky=W, pady=6)

        self.cleanModeCheckButton = ttk.Checkbutton(
            master=self,
            bootstyle=(WARNING, TOGGLE, SQUARE),
            text=' Logging',
            variable=self.enableLogging
        )
        self.cleanModeCheckButton.grid(row=4, column=0, sticky=W, pady=6)

        self.createCertificatesButton = ttk.Button(
            master=self,
            bootstyle=(DANGER, OUTLINE),
            text='Create Certificates',
            padding=9, width=18,
        )
        self.createCertificatesButton.grid(row=3, rowspan=2, column=2, sticky=E)

    def _selectImageFile(self):
        self._selectFile(self._imagePath, ("Image files",".img .png .jpeg .jpg"))
        self._callImagePathHandler()

    def _selectInfoFile(self):
        self._selectFile(self._infoFilePath, ("Info files",".txt .exel .xlsx"))
        fileExtension = self._infoFilePath.get().split('.')[-1]

        if fileExtension in {'txt'}:
            self.infoFileType = 'txt'
        elif fileExtension in {'exel', 'xlsx'}:
            self.infoFileType = 'exel'

        self._callInfoFilePathHandler()

    def _callImagePathHandler(self):
        if self.imageFunctionToCall is not None and self.imagePathEntry.validate():
            self.imageFunctionToCall(self._imagePath)

    def _callInfoFilePathHandler(self):
        if self.infoFileFunctionToCall is not None and self.infoPathEntry.validate():
            self.infoFileFunctionToCall(self._infoFilePath, self.infoFileType)
    
    def _selectFile(self, stringVar:tk.StringVar, filetype):
        stringVar.set(fd.askopenfilename(filetypes=(filetype,("All files","*.*"))))
 



class EmailInput(ttk.Labelframe):
    def __init__(
        self, 
        master, 
        enableTestMode=True,
        enableTwoLevelAuth=True
        ):
        super().__init__(master, text='Emailing Options', padding=(16, 10))

        self.columnconfigure(0, weight=1)        
        self.columnconfigure(1, weight=1)

        self.font = '-size 13'
        
        self.testEmail = ttk.StringVar()
        self.realEmail = ttk.StringVar()

        self.enableTestMode = ttk.BooleanVar(value=enableTestMode)
        self.enableTwoLevelAuth = ttk.BooleanVar(value=enableTwoLevelAuth)

        self.testEmailEntry = EntryWithPlaceholder(
            master=self,
            placeholder='Testing Email',
            font=self.font,
            textvariable=self.testEmail
        )
        self.testEmailEntry.grid(row=0, column=0, columnspan=2, pady=6, sticky=EW)

        self.testEmailEntry.bind('<Return>', lambda _: self.testEmailEntry.validate(), add='+')
        validators.addEmailValidation(self.testEmailEntry)

        self.realEmailEntry = EntryWithPlaceholder(
            master=self,
            placeholder='Real Email',
            font=self.font,
            textvariable=self.realEmail
        )
        self.realEmailEntry.grid(row=1, column=0, columnspan=2, pady=6, sticky=EW)

        self.realEmailEntry.bind('<Return>', lambda _: self.realEmailEntry.validate(), add='+')
        validators.addEmailValidation(self.realEmailEntry)

        ttk.Separator(self).grid(row=2, column=0, columnspan=2, pady=10, sticky=EW)

        self.testModeCheckButton = ttk.Checkbutton(
            master=self,
            bootstyle=(DANGER, TOGGLE, SQUARE),
            text=' Use Test Email',
            variable=self.enableTestMode
        )
        self.testModeCheckButton.grid(row=3, column=0, sticky=W, pady=6)

        self.twoLevelAuthCheckButton = ttk.Checkbutton(
            master=self,
            bootstyle=(WARNING, TOGGLE, SQUARE),
            text=' Two level Auth',
            variable=self.enableTwoLevelAuth
        )
        self.twoLevelAuthCheckButton.grid(row=4, column=0, sticky=W, pady=6)

        self.sendEmailsButton = ttk.Button(
            master=self,
            bootstyle=(DANGER, OUTLINE),
            text='Send Emails',
            padding=9, width=18,
        )
        self.sendEmailsButton.grid(row=3, rowspan=2, column=1, sticky=E)


class FontConfiguration(ttk.Frame):
    def __init__(self, master, font:ttk.font.Font=None):
        super().__init__(master)
        self.fontDialog = FontDialog(parent=master.master, title='Font Selection')

        self.showButton = ttk.Button(self, bootstyle=(DARK))

        self.ccoLabelFrame = ttk.Labelframe(
            master=self,
            text='Certificate Creation Options',
            padding=(14, 10, 0 ,10),
            width=330
        )
        self.ccoLabelFrame.pack(expand=YES, fill=Y, anchor=NE, side=RIGHT)

        self.ccoLabelFrame.rowconfigure(5, weight=1)

        self.selectFontButton = ttk.Button(
            master=self.ccoLabelFrame,
            bootstyle=(OUTLINE, WARNING),
            text='Select Font',
            padding=9,
            command=self._showFontDialog
        )
        self.selectFontButton.grid(row=0, column=0, sticky=EW, pady=6)

        # =-=-=-=-=-=- Colors Options -=-=-=-=-=--=-=

        self.colorLabel = ttk.Label(
            master=self.ccoLabelFrame,
            text='Select Font Color',
            bootstyle=(INVERSE, SECONDARY),
            anchor=CENTER, 
            font="-size 13"
        )
        self.colorLabel.grid(row=1, column=0, sticky=EW, pady=(7, 10))

        self.colorChooser = ColorChooser(master=self.ccoLabelFrame)
        self.colorChooser.grid(row=2, column=0, sticky=EW)

        self.fontChooser = FontChooser(master=self.ccoLabelFrame, bootstyle=WARNING)
        self.fontChooser.grid(row=3, column=0, sticky=EW)

        self.selectFontButton = ttk.Button(
            master=self.ccoLabelFrame,
            bootstyle=(OUTLINE, WARNING),
            text='Close',
            padding=9
        )
        self.selectFontButton.grid(row=6, column=0, sticky=EW, pady=6)

    def _showFontDialog(self):
        self.fontDialog.show()
        self.font = self.fontDialog._result
        self.fontChooser.meter.configure(amountused=self.font.cget('size'))

    def _hideWidget(self):
        self.ccoLabelFrame.pack_forget()
        self.showButton.pack(expand=YES, fill=BOTH)
    
    def _showWidget(self):
        self.showButton.pack_forget()
        self.ccoLabelFrame.pack(expand=YES, fill=Y, anchor=NE, side=RIGHT)


class App(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.rowconfigure(2, weight=1)

        self.columnconfigure(0, weight=1, minsize=450)
        self.columnconfigure(1, weight=1)

        self.modeSelection = ttk.Frame(self)
        self.modeSelection.grid(row=0, column=0, columnspan=3, sticky=NSEW)

        self.selectedModeLabel = ttk.Label(
            master=self.modeSelection, text="Certificates Creator", font="-size 24 -weight bold"
        )
        self.selectedModeLabel.pack(side=LEFT)

        self.mode = ttk.StringVar()
        self.modesSelectionLabel = ttk.Label(master=self.modeSelection, text="Select a mode:")
        self.modes = ('Certificates Creator', 'Email Sender')
        self.modesComboBox= ttk.Combobox(
            master=self.modeSelection,
            bootstyle=(LIGHT),
            state=READONLY,
            textvariable=self.mode,
            width=20,
            values=self.modes
        )
        self.modesComboBox.current(0)
        self.modesComboBox.pack(padx=10, side=RIGHT)
        self.modesSelectionLabel.pack(side=RIGHT)

        def changeMode(e):
            t = self.modesComboBox.get()
            self.selectedModeLabel.configure(text=t)

        self.modesComboBox.bind("<<ComboboxSelected>>", changeMode, add='+')
        self.mode.trace_add('write', self.changeMode)

        ttk.Separator(self).grid(row=1, column=0, columnspan=3, sticky=EW, pady=6)

        self.lFrame = ttk.Frame(self, padding=5)
        self.lFrame.grid(row=2, column=0, sticky=NSEW)

        self.mFrame = ttk.Frame(self, padding=5)
        self.mFrame.grid(row=2, column=1, sticky=NSEW)

        self.rFrame = ttk.Frame(self, padding=5)
        self.rFrame.grid(row=2, column=2, sticky=NSEW)

        # =-=-=-=-=-=- Default Options -=-=-=-=-=--=-=
        self.lFrame.rowconfigure(1, weight=1)
        self.lFrame.columnconfigure(0, weight=1)
        
        self.certificateOptions= InfoInput(master=self.lFrame)
        self.certificateOptions.grid(row=0, column=0, sticky=EW)

        self.emailingOptions = EmailInput(master=self.lFrame)
        
        self.certificateOptions.imageFunctionToCall = self.loadImage
        self.certificateOptions.infoFileFunctionToCall = self.proccessTxtFile

        self.canvas = ImageViewer(self.lFrame, 'assets/example.jpg', disableZoomOut=True)  # create widget
        self.canvas.grid(row=1, column=0, sticky=NSEW)

        # =-=-=-=-=-=-=-=-=- File Manager -=-=-=-=-=--=-=-=-=-=

        # notebook with table and text tabs
        self.fileManagerNotebook = ttk.Notebook(master=self.mFrame, bootstyle=LIGHT)
        self.fileManagerNotebook.pack(expand=YES, fill=BOTH, pady=(8, 0), padx=10)
        # enable key-binds for traversa;
        self.fileManagerNotebook.enable_traversal()

        self.filemanagerChildren = {}
        self.filemanagerChildren['Info File'] = TextEditor(self.fileManagerNotebook)
        self.filemanagerChildren['Name List'] = DataViewer(self.fileManagerNotebook, bootstyle=DARK)
        self.filemanagerChildren['Email'] = EmailCreator(self.fileManagerNotebook)
        self.filemanagerChildren['Logger'] = Logger(self.fileManagerNotebook) 

        for key, value in self.filemanagerChildren.items():
            self.fileManagerNotebook.add(value, text=key, sticky=NSEW)

        self.filemanagerChildren['Info File'].loadFile('requirements.txt')

        # =-=-=-=-=-=- Certificate Creation Options -=-=-=-=-=--=-=

        self.fontChooser = FontConfiguration(master=self.rFrame)
        self.fontChooser.pack(expand=YES, fill=Y, side=RIGHT)

    def proccessTxtFile(self, path:str, *_):
        logging = self.certificateOptions.enableLogging.get()
        # create and sort user list based on user name
        userList = sorted(dataFiltering.txtToList(path.get()), key=lambda a: a[1])
        # list with valid users
        self.userList = []
        # list with flagged users
        self.flaggedUserList = []

        # filter users based on their flags
        for item in userList:
            if item[2] == '':
                self.userList.append(item)
            else:
                self.flaggedUserList.append(item)

        # sort flaggedUserList based on flagIndex
        self.flaggedUserList = sorted(self.flaggedUserList, key=lambda a: a[2])

        for item in self.userList:
            self.filemanagerChildren['Name List'].insertItem([item[1], item[0]])

        for item in self.flaggedUserList:
            tag = ''
            # convert item flag to tree tag
            if item[2][0] == 'N':
                tag = 'flaggedName'
            elif item[2][0] == 'E':
                tag = 'flaggedEmail'

            self.filemanagerChildren['Name List'].insertItem([item[1], item[0]], tag)

        #dataFiltering.listToTxt(userList)
        self.loadFile('cleanFile.txt')

        # switch to DataViewer tab
        self.fileManagerNotebook.select(1)

    def loadFile(self, path:str, *_):
        """Load text file in the Text editor widget"""
        if os.path.exists(path):
            self.filemanagerChildren['Info File'].loadFile(path)

    def loadImage(self, path, *_):
        """Load image in the canvas widget"""
        # if the user closes the gui before selecting 
        # a file the path will be empty
        if os.path.exists(path.get()):
            self.canvas.loadImage(path.get())

    def changeToCertificateMode(self):
        self.emailingOptions.grid_remove()
        self.certificateOptions.grid(row=0, column=0, sticky=EW)

    def changeToEmailingMode(self):
        self.certificateOptions.grid_remove() 
        self.emailingOptions.grid(row=0, column=0, sticky=EW)

    def changeMode(self, *args):

        if self.mode.get() == 'Email Sender':
            self.changeToEmailingMode()
        else:
            self.changeToCertificateMode()


if __name__ == "__main__":

    window = ttk.Window("Certificates Creation", themename="darkly", minsize=(600, 565))
    style = ttk.Style()
    for color_label in style.colors:
        color = style.colors.get(color_label)
        print(color_label, color)

    window.geometry('1600x800')
    
    app = App(window)
    app.pack(expand=YES, fill=BOTH, padx=10, pady=10)

    app.bind('<Configure>', lambda e: print(e.height))
    window.mainloop()