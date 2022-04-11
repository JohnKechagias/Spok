import os
from functools import partial

import tkinter as tk
from tkinter import filedialog as fd
from tkinter import messagebox

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs.dialogs import FontDialog

from widgets import *

class FontChooser(ttk.Frame):
    def __init__(self, master, defaultFontSize=18, maxFontSize=50):
        super().__init__(master)
        
        self.meter = ttk.Meter(
            master=self,
            amounttotal=maxFontSize,
            metersize=150,
            amountused=defaultFontSize,
            stripethickness=8,
            subtext="Font Size",
            bootstyle=WARNING,
            interactive=False
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
        
        self.templatePath = tk.StringVar()
        self.infoFilePath = tk.StringVar()

        self.selectTemplateButton = ttk.Button(
            master=self,
            bootstyle=(DEFAULT),
            text='Select Template Image', 
            padding=9, width=20,
            command=partial(selectFile,
            self.templatePath, ("Image files",".img .png .jpeg .jpg"))
        )
        self.selectTemplateButton.grid(row=0, column=0, padx=6, pady=6)

        self.templatePathEntry = ttk.Entry(master=self, font=self.font, textvariable=self.templatePath)
        self.templatePathEntry.grid(row=0, column=1, columnspan=2, padx=6, pady=6, sticky=EW)

        self.selectInfoFileButton = ttk.Button(
            master=self,
            bootstyle=(DEFAULT),
            text='Select Info File',
            padding=9, width=20,
            command=partial(selectFile,
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


class App(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.rowconfigure(2, weight=1)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        # =-=-=-=-=-=- SETUP EVENTS -=-=-=-=-=-=-=-=
        self.modeSelection = ttk.Frame(self)
        self.modeSelection.grid(row=0, column=0, columnspan=3, sticky=NSEW)

        selectedModeLabel = ttk.Label(

            master=self.modeSelection, text="Certificates Creator", font="-size 24 -weight bold"
        )
        selectedModeLabel.pack(side=LEFT)

        modesSelectionLabel = ttk.Label(master=self.modeSelection, text="Select a mode:")
        modes = ('Certificates Creator', 'Email Sender')
        modesComboBox= ttk.Combobox(
            master=self.modeSelection,
            bootstyle=(DANGER),
            state=READONLY,
            width=20,
            values=modes
        )
        modesComboBox.current(0)
        modesComboBox.pack(padx=10, side=RIGHT)
        modesSelectionLabel.pack(side=RIGHT)

        def changeMode(e):
            t = modesComboBox.get()
            selectedModeLabel.configure(text=t)

        modesComboBox.bind("<<ComboboxSelected>>", changeMode)

        #ttk.Progressbar(root, orient=HORIZONTAL, bootstyle=(DARK), value=100).pack(fill=X, pady=10, padx=10)
        ttk.Separator(self).grid(row=1, column=0, columnspan=3, sticky=EW, pady=(0, 4))

        lFrame = ttk.Frame(self, padding=5)
        lFrame.grid(row=2, column=0, sticky=NSEW)

        mFrame = ttk.Frame(self, padding=5)
        mFrame.grid(row=2, column=1, sticky=NSEW)

        rFrame = ttk.Frame(self, padding=5)
        rFrame.grid(row=2, column=2, sticky=NSEW)

        # =-=-=-=-=-=- Default Options -=-=-=-=-=--=-=
        #topFrame = ttk.Frame(master=rframe)
        #topFrame.pack(side=TOP, expand=YES, fill=X, padx=10)

        #progressBar = ttk.Progressbar(master=topFrame, value=50)
        #progressBar.pack(side=BOTTOM, expand=YES, fill=X)

        self.certificateOptions= CertificateCreationInput(lFrame)
        self.certificateOptions.pack(expand=YES, fill=X, side=TOP)

        # =-=-=-=-=-=-=-=-=- File Manager -=-=-=-=-=--=-=-=-=-=

        # notebook with table and text tabs
        fileManagerNotebook = ttk.Notebook(master=mFrame, bootstyle=LIGHT)
        fileManagerNotebook.pack(expand=YES, fill=BOTH, pady=(8, 0), padx=10)

        filemanagerChilds = {}
        filemanagerChilds['Info File'] = TextEditor(fileManagerNotebook)
        filemanagerChilds['Name List'] = DataViewer(fileManagerNotebook, bootstyle=DARK)
        filemanagerChilds['Email'] = EmailCreator(fileManagerNotebook)
        filemanagerChilds['Logger'] = Logger(fileManagerNotebook) 

        for key, value in filemanagerChilds.items():
            fileManagerNotebook.add(value, text=key, sticky=NSEW)

        filemanagerChilds['Info File'].loadFile('requirements.txt')

        for i in range(30):
            filemanagerChilds['Name List'].insertItem(['John Kechagias', 'nice@gmail.com'])

        # =-=-=-=-=-=- Certificate Creation Options -=-=-=-=-=--=-=
        ccoLabelFrame = ttk.LabelFrame(
            master=rFrame,
            text='Certificate Creation Options',
            padding=10,
            width=300
        )
        ccoLabelFrame.pack(anchor=NE, side=RIGHT)

        selectFontButton = ttk.Button(
            master=ccoLabelFrame,
            text='Select Font',
            padding=9, width=18,
            command=selectFont
        )
        selectFontButton.pack(side=TOP, padx=6, pady=6)

        # =-=-=-=-=-=- Colors Options -=-=-=-=-=--=-=

        colorLabel = ttk.Label(master=ccoLabelFrame, text='Select Font Color', bootstyle=(INVERSE, LIGHT), anchor=CENTER, font="-size 13")
        colorLabel.pack(expand=YES, fill=X, pady=(7, 10), padx=6)

        colorChooser = ColorChooser(master=ccoLabelFrame)
        colorChooser.pack(expand=YES, fill=X)

        fontChooser = FontChooser(master=ccoLabelFrame)
        fontChooser.pack(expand=YES, fill=X)

        meterFrame = ttk.Frame(master=ccoLabelFrame)
        meterFrame.pack(expand=YES)

        # =-=-=-=-=-=- Image Options -=-=-=-=-=--=-=
        #templateLoader = ImageLoader(master=lframe, gifImagePath='assets/loading6.gif')
        #templateLoader.pack(expand=YES, anchor=SW)

        canvas = ImageViewer(lFrame, 'assets/nice.jpg')  # create widget
        canvas.pack(expand=YES, fill=BOTH, pady=(7, 0), anchor=SW)


def about():
    messagebox.showinfo('PythonGuides', 'Python Guides aims at providing best practical tutorials')

def selectFolder():
    folderpath = fd.askdirectory(initialdir=os.getcwd(), title='Select folder', mustexist=1)
    print(folderpath)

def selectFile(stringVar:tk.StringVar, filetype):
    stringVar.set(fd.askopenfilename(filetypes=(filetype,("All files","*.*"))))

def selectFont():
    x = FontDialog()
    x.show()


if __name__ == "__main__":
    window = ttk.Window("Certificates Creation", themename="darkly")

    style = ttk.Style()
    for color_label in style.colors:
        color = style.colors.get(color_label)
        print(color_label, color)

    window.geometry('1600x800')
    window.bind_class('TEntry', "<Return>", lambda event: print(type(event)))
    
    app = App(window)
    app.pack(expand=YES, fill=BOTH, padx=10, pady=10)
    window.mainloop()