import os
from functools import partial

import tkinter as tk
from tkinter import filedialog as fd
from tkinter import messagebox

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledFrame

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


class NewTextEditor(ttk.Frame):

    def __init__(
        self,
        master,
        padding=0,
        bootstyle=DEFAULT,
        autohide=False,
        vbar=True,
        hbar=False,
        **kwargs,
    ):
        super().__init__(master, padding=padding)

        # setup text widget
        self._numberedText = ttk.Text(master=self, width=3)
        self._text = ttk.Text(master=self, padx=50, **kwargs)
        self._hbar = None
        self._vbar = None

        # delegate text methods to frame
        for method in vars(ttk.Text).keys():
            if any(["pack" in method, "grid" in method, "place" in method]):
                pass
            else:
                setattr(self, method, getattr(self._text, method))

        # setup scrollbars
        if vbar:
            self._vbar = ttk.Scrollbar(
                master=self,
                bootstyle=bootstyle,
                command=self.__scrollBoth,
                orient=VERTICAL,
            )
            self._vbar.place(relx=1.0, relheight=1.0, anchor=NE)
            self._numberedText.configure(yscrollcommand=self.__updateScroll)
            self._text.configure(yscrollcommand=self.__updateScroll)
            self._text.bind('<Return>', self._showLineNumber)

        if hbar:
            self._hbar = ttk.Scrollbar(
                master=self,
                bootstyle=bootstyle,
                command=self._text.xview,
                orient=HORIZONTAL,
            )
            self._hbar.place(rely=1.0, relwidth=1.0, anchor=SW)
            self._text.configure(xscrollcommand=self._hbar.set, wrap="none")
        
        self._numberedText.pack(side=LEFT, fill=Y, expand=YES)
        self._text.pack(side=LEFT, fill=BOTH, expand=YES)

        # position scrollbars
        if self._hbar:
            self.update_idletasks()
            self._text_width = self.winfo_reqwidth()
            self._scroll_width = self.winfo_reqwidth()

        self.bind("<Configure>", self._on_configure)

        if autohide:
            self.autohide_scrollbar()
            self.hide_scrollbars()

    def _showLineNumber(self, *_):
        print(self._text.count('1.0', 'end', 'displaylines'))

    
    def __scrollBoth(self, action, position, type=None):
        self._text.yview_moveto(position)
        self._numberedText.yview_moveto(position)

    def __updateScroll(self, first, last, type=None):
        self._text.yview_moveto(first)
        self._numberedText.yview_moveto(first)
        self._vbar.set(first, last)

    def _combinedVerticalCallback(self, *args):
            self._text.yview(*args)
            self._numberedText.yview(*args)

    def _on_configure(self, *_):
        """Callback for when the configure method is used"""
        if self._hbar:
            self.update_idletasks()
            text_width = self.winfo_width()
            vbar_width = self._vbar.winfo_width()
            relx = (text_width - vbar_width) / text_width
            self._hbar.place(rely=1.0, relwidth=relx)


class textEditor(ScrolledFrame):

    def __init__(self, master, defaultFont=0, defaultFontSize=18):
            super().__init__(master=master, autohide=True, padding=0)

            self.columnconfigure(index=0, weight=1)
            self.rowconfigure(index=0, weight=1)

            self.numberedLines = ttk.Text(master=self, width=3)
            self.numberedLines.tag_configure('line', justify='right')
            #self.numberedLines.config(state=DISABLED)
            #self.numberedLines.pack(fill=BOTH, expand=YES, side=LEFT)

            self.scrolledText = ttk.Text(master=self)
            self.scrolledText.grid(row=0,column=0, sticky=NSEW)

def CreateApp(master):

    root = ttk.Frame(master, padding=10)
    root.pack(fill=BOTH, expand=YES)

    # =-=-=-=-=-=- SETUP EVENTS -=-=-=-=-=-=-=-=

    modeSelection = ttk.Frame(root, padding=(10, 10, 10, 0))
    modeSelection.pack(fill=X)

    selectedModeLabel = ttk.Label(
        master=modeSelection, text="Certificates Creation", font="-size 24 -weight bold"
    )
    selectedModeLabel.pack(side=LEFT)

    modesSelectionLabel = ttk.Label(master=modeSelection, text="Select a mode:")
    modes = ('Certificates Creation', 'Email With Attachment', 'Email Without Attachment')
    modesComboBox= ttk.Combobox(
        master=modeSelection,
        bootstyle=(DANGER),
        state=READONLY,
        values=modes
    )
    modesComboBox.current(0)
    modesComboBox.pack(padx=10, side=RIGHT)
    modesSelectionLabel.pack(side=RIGHT)

    def changeMode(e):
        t = modesComboBox.get()
        selectedModeLabel.configure(text=t)

    modesComboBox.bind("<<ComboboxSelected>>", changeMode)

    ttk.Separator(root).pack(fill=X, pady=10, padx=10)

    lframe = ttk.Frame(root, padding=5)
    lframe.pack(side=LEFT, fill=BOTH, expand=YES)

    rframe = ttk.Frame(root, padding=5)
    rframe.pack(side=RIGHT, fill=BOTH, expand=YES)

    # =-=-=-=-=-=- Default Options -=-=-=-=-=--=-=

    widgetsLabelFrame = ttk.LabelFrame(master=lframe, text='Options', padding=(10,10,0,10))
    widgetsLabelFrame.pack(anchor=NW)

    templatePath = tk.StringVar()
    infoFilePath = tk.StringVar()

    selectTemplateButton = ttk.Button(
        master=widgetsLabelFrame,
        bootstyle=(DEFAULT),
        text='Select Template Image', 
        padding=9, width=20,
        command=partial(selectFile,
        templatePath, ("Image files",".img .png .jpeg .jpg"))
    )
    selectTemplateButton.grid(row=0, column=0, padx=6, pady=6)

    templatePathEntry = ttk.Entry(master=widgetsLabelFrame, font="-size 13", textvariable=templatePath, width=41)
    templatePathEntry.grid(row=0, column=1, columnspan=2, padx=(6, 20), pady=6)

    selectInfoFileButton = ttk.Button(
        master=widgetsLabelFrame,
        bootstyle=(DEFAULT),
        text='Select Info File',
        padding=9, width=20,
        command=partial(selectFile,
        infoFilePath, ("Info files",".txt .exel .xlsx"))
    )
    selectInfoFileButton.grid(row=1, column=0, padx=6, pady=6)

    InfoPathEntry = ttk.Entry(master=widgetsLabelFrame, font="-size 13", textvariable=infoFilePath, width=41)
    InfoPathEntry.grid(row=1, column=1, columnspan=2, padx=(6, 20), pady=6)

    ttk.Separator(widgetsLabelFrame).grid(row=2, column=0, columnspan=3, pady=10, sticky=EW)

    errorCheckModeCheckButton = ttk.Checkbutton(
        master=widgetsLabelFrame,
        bootstyle=(SUCCESS, TOGGLE, ROUND),
        text='Error Checking'
    )
    errorCheckModeCheckButton.grid(row=3, column=0, sticky=W, pady=6)

    cleanModeCheckButton = ttk.Checkbutton(
        master=widgetsLabelFrame,
        bootstyle=(SUCCESS, TOGGLE, ROUND),
        text='Logging'
    )
    cleanModeCheckButton.grid(row=4, column=0, sticky=W, pady=6)

    cleanInfoFileButton = ttk.Button(
        master=widgetsLabelFrame,
        bootstyle=(LIGHT),
        text='Clean Info File',
        padding=9, width=18,
    )
    cleanInfoFileButton.grid(row=3, rowspan=2, column=2, sticky=E, padx=(0, 20))

    # =-=-=-=-=-=- File Manager Controls -=-=-=-=-=--=-=
    fileManagerFrame = ttk.Frame(master=rframe)
    fileManagerFrame.pack(side=LEFT, expand=YES, fill=BOTH)

    
    fileManagerControlsFrame = ttk.Frame(master=fileManagerFrame, padding=(10,0,10,20))
    fileManagerControlsFrame.pack(side=TOP)


    createCertificatesButton = ttk.Button(
        master=fileManagerControlsFrame,
        bootstyle=(DANGER),
        text='Create Certificates',
        padding=10, width=18,
    )
    createCertificatesButton.grid(row=0, column=0, padx=10)

    sendEmailButton = ttk.Button(
        master=fileManagerControlsFrame,
        bootstyle=(DANGER),
        text='Send Email',
        padding=10, width=18,
    )

    sendEmailButton.grid(row=0, column=2, padx=10)

    successBar = ttk.Floodgauge(master=fileManagerControlsFrame, bootstyle=LIGHT, text="0/100")
    successBar.grid(row=0, column=1, sticky=EW, padx=10)



    # =-=-=-=-=-=-=-=-=- File Manager -=-=-=-=-=--=-=-=-=-=

    # # notebook with table and text tabs
    fileManagerNotebook = ttk.Notebook(master=fileManagerFrame, bootstyle=(LIGHT))
    fileManagerNotebook.pack(side=TOP, expand=YES, fill=BOTH, padx=10)
    fileManagerNotebook.add(
        NewTextEditor(fileManagerNotebook),
        text="Info File", sticky=NSEW)
    fileManagerNotebook.add(
        child=ttk.Label(fileManagerNotebook, text="A notebook tab."), text="Email", sticky=NW
    )
    fileManagerNotebook.add(ttk.Frame(fileManagerNotebook), text="Emailing List")
    fileManagerNotebook.add(ttk.Frame(fileManagerNotebook), text="Tab 4")
    fileManagerNotebook.add(ttk.Frame(fileManagerNotebook), text="Tab 5")

    # =-=-=-=-=-=- Certificate Creation Options -=-=-=-=-=--=-=

    ccoLabelFrame = ttk.LabelFrame(
        master=rframe,
        text='Certificate Creation Options',
        padding=10,
        width=300
    )
    ccoLabelFrame.pack(anchor=NE, side=RIGHT, padx=10)

    selectFontButton = ttk.Button(
        master=ccoLabelFrame,
        text='Select Font',
        padding=9, width=18,
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
    templateLoader = ImageLoader(master=lframe, gifImagePath='assets/loading6.gif')
    templateLoader.pack(expand=YES, anchor=SW)


def about():
    messagebox.showinfo('PythonGuides', 'Python Guides aims at providing best practical tutorials')

def selectFolder():
    folderpath = fd.askdirectory(initialdir=os.getcwd(), title='Select folder', mustexist=1)
    print(folderpath)

def selectFile(stringVar:tk.StringVar, filetype):
    stringVar.set(fd.askopenfilename(filetypes=(filetype,("All files","*.*"))))


if __name__ == "__main__":
    app = ttk.Window("Certificates Creation", themename="darkly")
    app.geometry('1600x800')
    app.bind_class('TEntry', "<Return>", lambda event: print(type(event)))
    CreateApp(master=app)
    app.mainloop()