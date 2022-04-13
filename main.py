import os
from functools import partial

import tkinter as tk
from tkinter import filedialog as fd

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs.dialogs import FontDialog
from widgets import *

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


class CertificateCreationInput(ttk.Labelframe):
    def __init__(self, master):
        super().__init__(master, text='Options', padding=10)

        self.columnconfigure(1, weight=1)        
        self.columnconfigure(2, weight=1)

        self.font = '-size 13'
        
        self.imagePath = tk.StringVar()
        self.infoFilePath = tk.StringVar()

        self.selectTemplateButton = ttk.Button(
            master=self,
            bootstyle=(DEFAULT),
            text='Select Template Image', 
            padding=9, width=20,
            command=partial(self.selectFile,
            self.imagePath, ("Image files",".img .png .jpeg .jpg"))
        )
        self.selectTemplateButton.grid(row=0, column=0, padx=6, pady=6)

        self.templatePathEntry = ttk.Entry(master=self, font=self.font, textvariable=self.imagePath)
        self.templatePathEntry.grid(row=0, column=1, columnspan=2, padx=6, pady=6, sticky=EW)

        self.selectInfoFileButton = ttk.Button(
            master=self,
            bootstyle=(DEFAULT),
            text='Select Info File',
            padding=9, width=20,
            command=partial(self.selectFile,
            self.infoFilePath, ("Info files",".txt .exel .xlsx"))
        )
        self.selectInfoFileButton.grid(row=1, column=0, padx=6, pady=6)

        self.infoPathEntry = ttk.Entry(master=self, font=self.font, textvariable=self.infoFilePath)
        self.infoPathEntry.grid(row=1, column=1, columnspan=2, padx=6, pady=6, sticky=EW)

        ttk.Separator(self).grid(row=2, column=0, columnspan=3, pady=10, sticky=EW)

        self.errorCheckModeCheckButton = ttk.Checkbutton(
            master=self,
            bootstyle=(SUCCESS, TOGGLE, ROUND),
            text='Error Checking'
        )
        self.errorCheckModeCheckButton.grid(row=3, column=0, sticky=W, pady=6)

        self.cleanModeCheckButton = ttk.Checkbutton(
            master=self,
            bootstyle=(SUCCESS, TOGGLE, ROUND),
            text='Logging'
        )
        self.cleanModeCheckButton.grid(row=4, column=0, sticky=W, pady=6)

        self.cleanInfoFileButton = ttk.Button(
            master=self,
            bootstyle=(LIGHT),
            text='Clean Info File',
            padding=9, width=18,
        )
        self.cleanInfoFileButton.grid(row=3, rowspan=2, column=2, sticky=E, padx=6)

    def selectFolder(self):
        folderpath = fd.askdirectory(initialdir=os.getcwd(), title='Select folder', mustexist=1)

    def selectFile(self, stringVar:tk.StringVar, filetype):
        stringVar.set(fd.askopenfilename(filetypes=(filetype,("All files","*.*"))))


class App(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.rowconfigure(2, weight=1)

        self.columnconfigure(0, weight=2, minsize=400)
        self.columnconfigure(1, weight=1)

        self.modeSelection = ttk.Frame(self)
        self.modeSelection.grid(row=0, column=0, columnspan=3, sticky=NSEW)

        self.selectedModeLabel = ttk.Label(

            master=self.modeSelection, text="Certificates Creator", font="-size 24 -weight bold"
        )
        self.selectedModeLabel.pack(side=LEFT)

        self.modesSelectionLabel = ttk.Label(master=self.modeSelection, text="Select a mode:")
        self.modes = ('Certificates Creator', 'Email Sender')
        self.modesComboBox= ttk.Combobox(
            master=self.modeSelection,
            bootstyle=(LIGHT),
            state=READONLY,
            width=20,
            values=self.modes
        )
        self.modesComboBox.current(0)
        self.modesComboBox.pack(padx=10, side=RIGHT)
        self.modesSelectionLabel.pack(side=RIGHT)

        def changeMode(e):
            t = self.modesComboBox.get()
            self.selectedModeLabel.configure(text=t)

        self.modesComboBox.bind("<<ComboboxSelected>>", changeMode)

        ttk.Separator(self).grid(row=1, column=0, columnspan=3, sticky=EW, pady=6)

        self.lFrame = ttk.Frame(self, padding=5)
        self.lFrame.grid(row=2, column=0, sticky=NSEW)

        self.mFrame = ttk.Frame(self, padding=5)
        self.mFrame.grid(row=2, column=1, sticky=NSEW)

        self.rFrame = ttk.Frame(self, padding=5)
        self.rFrame.grid(row=2, column=2, sticky=NSEW)

        # =-=-=-=-=-=- Default Options -=-=-=-=-=--=-=

        #topFrame = ttk.Frame(master=rframe)
        #topFrame.pack(side=TOP, expand=YES, fill=X, padx=10)

        #progressBar = ttk.Progressbar(master=topFrame, value=50)
        #progressBar.pack(side=BOTTOM, expand=YES, fill=X)
        self.lFrame.rowconfigure(1, weight=1)

        self.lFrame.columnconfigure(0, weight=1)
        
        self.certificateOptions= CertificateCreationInput(self.lFrame)
        self.certificateOptions.grid(row=0, column=0, sticky=EW)

        self.certificateOptions.imagePath.trace('w', 
            partial(self.loadImage, self.certificateOptions.imagePath))

        self.certificateOptions.infoFilePath.trace('w', 
            partial(self.loadFile, self.certificateOptions.infoFilePath))

        self.canvas = ImageViewer(self.lFrame, 'assets/nice.jpg')  # create widget
        self.canvas.grid(row=1, column=0, sticky=NSEW)

        # =-=-=-=-=-=-=-=-=- File Manager -=-=-=-=-=--=-=-=-=-=

        # notebook with table and text tabs
        self.fileManagerNotebook = ttk.Notebook(master=self.mFrame, bootstyle=LIGHT)
        self.fileManagerNotebook.pack(expand=YES, fill=BOTH, pady=(8, 0), padx=10)

        self.filemanagerChildren = {}
        self.filemanagerChildren['Info File'] = TextEditor(self.fileManagerNotebook)
        self.filemanagerChildren['Name List'] = DataViewer(self.fileManagerNotebook, bootstyle=DARK)
        self.filemanagerChildren['Email'] = EmailCreator(self.fileManagerNotebook)
        self.filemanagerChildren['Logger'] = Logger(self.fileManagerNotebook) 

        for key, value in self.filemanagerChildren.items():
            self.fileManagerNotebook.add(value, text=key, sticky=NSEW)

        self.filemanagerChildren['Info File'].loadFile('requirements.txt')

        for _ in range(30):
            self.filemanagerChildren['Name List'].insertItem(['John Kechagias', 'nice@gmail.com'])

        # =-=-=-=-=-=- Certificate Creation Options -=-=-=-=-=--=-=

        self.ccoLabelFrame = ttk.LabelFrame(
            master=self.rFrame,
            text='Certificate Creation Options',
            padding=10,
            width=340
        )
        self.ccoLabelFrame.pack(anchor=NE, side=RIGHT)

        self.selectFontButton = ttk.Button(
            master=self.ccoLabelFrame,
            bootstyle=(OUTLINE, WARNING),
            text='Select Font',
            padding=9,
            command=selectFont
        )
        self.selectFontButton.pack(expand=YES, fill=X, side=TOP, pady=6)

        # =-=-=-=-=-=- Colors Options -=-=-=-=-=--=-=

        self.colorLabel = ttk.Label(master=self.ccoLabelFrame, text='Select Font Color', bootstyle=(INVERSE, SECONDARY), anchor=CENTER, font="-size 13")
        self.colorLabel.pack(expand=YES, fill=X, pady=(7, 10))

        self.colorChooser = ColorChooser(master=self.ccoLabelFrame)
        self.colorChooser.pack(expand=YES, fill=X)

        self.fontChooser = FontChooser(master=self.ccoLabelFrame, bootstyle=WARNING)
        self.fontChooser.pack(expand=YES, fill=X)

        self.meterFrame = ttk.Frame(master=self.ccoLabelFrame)
        self.meterFrame.pack(expand=YES, fill=X)

    def loadFile(self, path:str, *_):
        """Load text file in the Text editor widget"""
        if path.get() != '':
            self.filemanagerChildren['Info File'].loadFile(path.get())

    def loadImage(self, path, *_):
        """Load image in the canvas widget"""
        # if the user closes the gui before selecting 
        # a file the path will be empty
        if path.get() != '':
            self.canvas.loadImage(path.get())


def selectFont():
    x = FontDialog()
    x.show()


if __name__ == "__main__":

    window = ttk.Window("Certificates Creation", themename="darkly", minsize=(600, 400))
    style = ttk.Style()
    for color_label in style.colors:
        color = style.colors.get(color_label)
        print(color_label, color)

    window.geometry('1600x800')
    window.bind_class('TEntry', "<Return>", lambda event: print(type(event)))
    
    app = App(window)
    app.pack(expand=YES, fill=BOTH, padx=10, pady=10)
    window.mainloop()