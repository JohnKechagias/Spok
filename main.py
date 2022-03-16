import os
from functools import partial

from pathlib import Path
from itertools import cycle

from PIL import Image, ImageTk, ImageSequence

import tkinter as tk
from tkinter import filedialog as fd
from tkinter import messagebox

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledFrame

# USE PIL FOR IMAGE RESIZE
class TemplateLoader(ttk.LabelFrame):
    def __init__(self, master, loadingImage = 'assets/loading6.gif', defaultImage = None):
        super().__init__(master, text="Template Image")

        # the states that the template loader can be in.
        LOADING = False  # Template Loader doesn't have an image and the loading GIF is active.
        ACTIVE = True    # Template Loader has a loaded image and the loading GIF is inactive.

        loadingImagePath = Path(__file__).parent / loadingImage

        self.baseImage = None
        self.currentImage = None
        self.imageState = LOADING

        # setup loading image
        # open the GIF and create a cycle iterator
        with Image.open(loadingImagePath) as im:
            # create a sequence
            sequence = ImageSequence.Iterator(im)
            images = [ImageTk.PhotoImage(s) for s in sequence]
            self.loadingImageCycle = cycle(images)

            # length of each frame
            self.framerate = im.info["duration"]
        
        self.imageContainer = ttk.Label(self)
        self.imageContainer.pack(expand=YES, anchor=SW)

        # if we have a saved image load it else, show the
        # loading image
        if defaultImage == None:
            self.startLoadingGif()
        else:
            self.loadImage(defaultImage)


        self.imageContainer.bind('<Button-5>', lambda e: self.zoom_at(e.x, e.y, 1.2))  # zoom for Linux, wheel scroll down
        self.imageContainer.bind('<Button-4>', lambda e: self.zoom_at(e.x, e.y, 1.2))  # zoom for Linux, wheel scroll up

    def nextFrame(self):
        """Update the image for each frame"""
        self.imageContainer.configure(image=next(self.loadingImageCycle))
        self.after(self.framerate, self.nextFrame)

    def loadImage(self, imagePath):
        self.baseImage = Image.open(imagePath)
        self.currentImage = self.baseImage.copy()
        self.shownLimage = ImageTk.PhotoImage(self.currentImage)
        self.imageContainer.configure(image=self.shownLimage)

    def unloadImage(self):
        self.baseImage = None
        self.currentImage = None
        self.startLoadingGif()

    def startLoadingGif(self):
        self.imageContainer.configure(image=next(self.loadingImageCycle))
        self.updateGifFunc = self.after(self.framerate, self.nextFrame)

    def stopLoadingGif(self):
        self.after_cancel(self.updateGifFunc)

    def zoom_at(self, x, y, zoom):
        width, height = self.currentImage.size
        newHWidth = width / (zoom * 2)
        newHHeight = height / (zoom * 2)

        cropBox = (x - newHWidth, y - newHHeight,
                   x + newHWidth, y + newHHeight)
        img = self.currentImage.crop(cropBox)
        self.currentImage = img.resize((width, height), Image.LANCZOS)
        self.shownLimage = ImageTk.PhotoImage(self.currentImage)
        self.imageContainer.configure(image=self.shownLimage)


class ImageLoader(ttk.LabelFrame):
    def __init__(self, master, imagePath = 'assets/nice.jpg', zoom=0.5):
        super().__init__(master, text="Template Image")

        self.imageContainer = ttk.Label(self)
        self.imageContainer.pack(expand=YES, anchor=CENTER)

        self.imageEdits = []
        self.zoom = zoom
        # zoom in count
        self.zoomLevel = 0

        image = Image.open(imagePath)
        self.setImage(image)
        self.__setCurrentImage(image)

        self.imageContainer.bind('<Button-4>', lambda e: self.__zoomIn(e.x, e.y))  # zoom for Linux, wheel scroll up
        self.imageContainer.bind('<Button-5>', lambda _: self.__zoomOut())  # zoom for Linux, wheel scroll down

    def setImage(self, image:Image.Image):
        """Sets Imageloaders image.

        Args:
            image (PIL.Image.Image): image object to load.
        """
        self.originalImage = image
        self.imageSize = self.originalImage.size

        centerCoords = (self.originalImage.size[0] / 2, self.originalImage.size[1] / 2)

        self.imageEdits.clear()
        self.imageEdits.append(centerCoords)

        width = self.zoom * self.originalImage.size[0]
        height = self.zoom * self.originalImage.size[1]
        self.zoomedImageSize = (width, height)

    def __setCurrentImage(self, image:Image.Image):
        """Sets ImagesLoaders shown image.

        Args:
            image (PIL.Image.Image): image object to display.
        """
        self.currentImage = image
        self.tkImage = ImageTk.PhotoImage(self.currentImage)
        self.imageContainer.configure(image=self.tkImage)

    def __zoomIn(self, x, y):
        coords, box = self.__normalizeCoordinates(x, y)

        zoomMultiplier = self.zoom ** self.zoomLevel
        coords = self.__coordDistance(self.imageEdits[0], coords, zoomMultiplier)
        self.imageEdits.append(coords)

        zoomedInImage = self.currentImage.resize(
            self.imageSize, 
            resample=Image.NEAREST, 
            box=box
        )
        
        self.__setCurrentImage(zoomedInImage)
        self.zoomLevel += 1

    def __normalizeCoordinates(self, x, y):
        xCoordinates = [x - self.zoomedImageSize[0] / 2, x + self.zoomedImageSize[0] / 2]
        yCoordinates = [y - self.zoomedImageSize[1] / 2, y + self.zoomedImageSize[1] / 2]

        for val in xCoordinates:
            xDisplaceValue = 0

            if val < 0:
                xDisplaceValue = abs(val)
            elif val > self.imageSize[0]:
                xDisplaceValue = self.imageSize[0] - val

            xCoordinates = [x + xDisplaceValue for x in xCoordinates]
            x += xDisplaceValue

        for val in yCoordinates:
            yDisplaceValue = 0

            if val < 0:
                yDisplaceValue = abs(val)
            elif val > self.imageSize[1]:
                yDisplaceValue = self.imageSize[1] - val

            yCoordinates = [x + yDisplaceValue for x in yCoordinates]
            y += yDisplaceValue

        return ((x, y), [xCoordinates[0], yCoordinates[0], xCoordinates[1], yCoordinates[1]])

    def __zoomOut(self):
        if self.zoomLevel == 0:
            return
        elif self.zoomLevel == 1:
            self.imageEdits.pop()
            zoomedOutImage = self.originalImage
        else:
            self.imageEdits.pop()
            coords = tuple(map(sum, zip(*self.imageEdits)))
            zoomLevel = self.zoom ** (self.zoomLevel - 2)
            box = self.__getBox(coords[0], coords[1], zoomLevel)

            zoomedOutImage = self.originalImage.resize(
                self.imageSize, 
                resample=Image.NEAREST, 
                box=box
            )

        self.__setCurrentImage(zoomedOutImage)
        self.zoomLevel -= 1

    def __getBox(self, x, y, sizeMultiplier=1):
        """Get box coordinates around the center (x, y).
        The size of the box is zoomedImageSize and is shrinked
        or enlarged based on the sizeMultiplier.

        Args:
            x (float): x center coordinate
            y (float): y center coordinate
            sizeMultiplier (int, optional): can change the box size. Defaults to 1.

        Returns:
            list: box coordinates (left, top, right, bottom)
        """
        return [x - sizeMultiplier * (self.zoomedImageSize[0] / 2), y - sizeMultiplier * (self.zoomedImageSize[1] / 2),
                x + sizeMultiplier * (self.zoomedImageSize[0] / 2), y + sizeMultiplier * (self.zoomedImageSize[1] / 2)]

    def __coordDistance(self, center, point, multiplier=1):
        x = point[0] - center[0]
        y = point[1] - center[1]
        return (multiplier *  x, multiplier * y)


class ColorChooser(ttk.Frame):
    def __init__(self, master, defaultColor:tuple = (75, 75, 75)):
        super().__init__(master)

        # color is a dict and each color channel is also a dict
        self.color = {'red': {}, 'green': {}, 'blue': {}}
        self.color['red']['style'] = DANGER
        self.color['green']['style'] = SUCCESS
        self.color['blue']['style'] = DEFAULT

        # theshold that dictates the color of the colored button
        # foreground. If the button is dark, the fg is bright etc.
        self.foregroundThreshold = 300

        # is used to lock and unlock event handlers like a mutex
        self.update_in_progress = False

        for i, (channelName, channel) in enumerate(self.color.items()):
            channel['value'] = tk.IntVar(value=defaultColor[i])

            channel['frame'] = ttk.Frame(master=self)
            channel['frame'].pack(fill=X, expand=YES, pady=3)

            channel['entry'] = ttk.Entry(master=channel['frame'],
                width=3,
                textvariable=channel['value']
            )
            channel['entry'].pack(side=LEFT)

            channel['scale'] = ttk.Scale(
                master=channel['frame'],
                orient=HORIZONTAL,
                bootstyle=channel['style'],
                variable=channel['value'],
                value=75, to=255
            )
            channel['scale'].pack(side=RIGHT, fill=X, expand=YES, padx=6, pady=6)

            channel['value'].trace("w", partial(self.updateColorValue, channelName))
            channel['entry'].bind('<Any-KeyPress>', partial(self.keysPressed, channel['value']), add='+')

        coloredButtonFrame = ttk.Frame(master=self, border=3, bootstyle=DARK)
        coloredButtonFrame.pack(fill=BOTH, expand=YES, pady=10)

        self.coloredButton = tk.Button(
            master=coloredButtonFrame,
            autostyle=False,
            foreground='white',
            activeforeground='white',
            background=self.getColorCode(),
            activebackground=self.getColorCode(),
            text=self.getColorCode(),
            bd=0,
            highlightthickness=0
        )
        self.coloredButton.pack(side=TOP, expand=YES, fill=X)

    def updateColorValue(self, colorName, *_):
        # normalize and update color value
        if self.update_in_progress == True: return
        try:
            tempValue = self.color[colorName]['value'].get()
        except:
            return

        self.update_in_progress = True

        # round the float value
        self.color[colorName]['value'].set(round(tempValue))
        self.updateColoredButton()
        
        self.update_in_progress = False

    def updateColoredButton(self):
        # sum of RGB channel values
        sumOfColorValues = sum(self.getColorTuple())
        colorCode = self.getColorCode()

        if sumOfColorValues > self.foregroundThreshold:
            self.coloredButton.configure(foreground='black', activeforeground='black')
        else:
            self.coloredButton.configure(foreground='white', activeforeground='white')
        self.coloredButton.configure(background=colorCode, activebackground=colorCode, text=colorCode)
    
    def getColorTuple(self):
        return (i['value'].get() for i in self.color.values())
    
    def setColor(self, color:tuple):
        for i, channel in enumerate(self.color.values()):
            channel['value'].set(color[i])

    def getColorCode(self):
        colorRGBTuple = self.getColorTuple()
        return _from_rgb(colorRGBTuple)

    def _from_rgb(rgb):
        """translates an rgb tuple of int to a tkinter friendly color code"""
        r, g, b = rgb
        return f'#{r:02x}{g:02x}{b:02x}'

    def keysPressed(topWidget, entryTextVar, event:tk.Event):
        if event.keysym == 'Right':
            # check if the cursor is in the end of the word
            # (don't want to fire the event if the user just wants
            # to move the cursor)
            if event.widget.index(INSERT) == len(str(entryTextVar.get())):
                entryTextVar.set(entryTextVar.get() + 1)
        elif event.keysym == 'Left':
            # check if the cursor is at the start of the word
            # (don't want to fire the event if the user just wants
            # to move the cursor)
            if event.widget.index(INSERT) == 0:
                entryTextVar.set(entryTextVar.get() - 1)


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
        padding=9, width=18,
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
        padding=9, width=18,
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
    templateLoader = ImageLoader(master=lframe)
    templateLoader.pack(expand=YES, anchor=SW)



def about():
    messagebox.showinfo('PythonGuides', 'Python Guides aims at providing best practical tutorials')

def selectFolder():
    folderpath = fd.askdirectory(initialdir=os.getcwd(), title='Select folder', mustexist=1)
    print(folderpath)

def selectFile(stringVar:tk.StringVar, filetype):
    stringVar.set(fd.askopenfilename(filetypes=(filetype,("All files","*.*"))))
    
def _from_rgb(rgb):
    """translates an rgb tuple of int to a tkinter friendly color code
    """
    r, g, b = rgb
    return f'#{r:02x}{g:02x}{b:02x}'
        
if __name__ == "__main__":
    app = ttk.Window("Certificates Creation", themename="darkly")
    app.geometry('1600x800')
    app.bind_class('TEntry', "<Return>", lambda event: print(type(event)))
    CreateApp(master=app)
    app.mainloop()