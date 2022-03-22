import tkinter as tk
import warnings

from PIL import Image, ImageTk, ImageSequence
from itertools import cycle

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from helperFuncs import containToRange
import numpy as np



class ImageLoader(ttk.LabelFrame):
    def __init__(self, master, gifImagePath, imagePath=None, zoom=0.5):
        super().__init__(master, text='Template Image')

        self.imageContainer = ttk.Label(self)
        self.imageContainer.pack(expand=YES, anchor=CENTER)

        self.imageEdits = []
        self.zoom = zoom
        self.zoomLevel = 0  # zoom count

        # setup loading image
        # open the GIF and create a cycle iterator
        with Image.open(gifImagePath) as gif:
            # create a sequence
            sequence = ImageSequence.Iterator(gif)
            images = [ImageTk.PhotoImage(s) for s in sequence]
            self.loadingImageCycle = cycle(images)
            # length of each frame
            self.framerate = gif.info["duration"]

        image = Image.open(imagePath)
        self.loadImage(image)

        self.imageContainer.bind('<Button-4>', self._zoomIn)  # zoom for Linux, wheel scroll up
        self.imageContainer.bind('<Button-5>', self._zoomOut)  # zoom for Linux, wheel scroll down

    def loadImage(self, image:Image.Image):
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

        self._setCurrentImage(image)

    def unloadImage(self):
        self.originalImage = None
        self._startGif()

    def _setCurrentImage(self, image:Image.Image):
        """Sets ImagesLoaders shown image.

        Args:
            image (PIL.Image.Image): image object to display.
        """
        self.currentImage = image
        self.tkImage = ImageTk.PhotoImage(self.currentImage)
        self.imageContainer.configure(image=self.tkImage)

    def _startGif(self):
        self.imageContainer.configure(image=next(self.loadingImageCycle))
        self.updateGifFunc = self.after(self.framerate, self._nextFrame)

    def _stopGif(self):
        self.after_cancel(self.updateGifFunc)

    def _nextFrame(self):
        """Update the image for each frame"""
        self.imageContainer.configure(image=next(self.loadingImageCycle))
        self.after(self.framerate, self._nextFrame)

    def _zoomIn(self, e:tk.Event):
        coords, box = self._normalizeCoordinates(e.x, e.y)

        zoomMultiplier = self.zoom ** self.zoomLevel
        coords = self._coordDistance(self.imageEdits[0], coords, zoomMultiplier)
        self.imageEdits.append(coords)

        zoomedInImage = self.currentImage.resize(
            self.imageSize, 
            resample=Image.NEAREST, 
            box=box
        )
        
        self._setCurrentImage(zoomedInImage)
        self.zoomLevel += 1

    def _normalizeCoordinates(self, x, y):
        xCoordinates = [x - self.zoomedImageSize[0] / 2, x + self.zoomedImageSize[0] / 2]
        yCoordinates = [y - self.zoomedImageSize[1] / 2, y + self.zoomedImageSize[1] / 2]

        for val in xCoordinates:
            xDisplaceValue = containToRange((0, self.imageSize[0]), val)

            xCoordinates = [x + xDisplaceValue for x in xCoordinates]
            x += xDisplaceValue

        for val in yCoordinates:
            yDisplaceValue = containToRange((0, self.imageSize[1]), val)

            yCoordinates = [x + yDisplaceValue for x in yCoordinates]
            y += yDisplaceValue

        return ((x, y), [xCoordinates[0], yCoordinates[0], xCoordinates[1], yCoordinates[1]])

    def _zoomOut(self, _):
        if self.zoomLevel == 0:
            return
        elif self.zoomLevel == 1:
            self.imageEdits.pop()
            zoomedOutImage = self.originalImage
        else:
            self.imageEdits.pop()
            coords = tuple(map(sum, zip(*self.imageEdits)))
            zoomLevel = self.zoom ** (self.zoomLevel - 2)
            box = self._getBox(coords[0], coords[1], zoomLevel)

            zoomedOutImage = self.originalImage.resize(
                self.imageSize, 
                resample=Image.NEAREST, 
                box=box
            )

        self._setCurrentImage(zoomedOutImage)
        self.zoomLevel -= 1

    def _getBox(self, x, y, sizeMultiplier=1):
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

    def _coordDistance(self, center, point, multiplier=1):
        x = point[0] - center[0]
        y = point[1] - center[1]
        return (multiplier *  x, multiplier * y)


class AutoScrollbar(ttk.Scrollbar):
    """ A scrollbar that hides itself if it's not needed. Works only for grid geometry manager """
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.grid_remove()
        else:
            self.grid()
            ttk.Scrollbar.set(self, lo, hi)

    def pack(self, **kw):
        raise ttk.TclError('Cannot use pack with the widget ' + self.__class__.__name__)

    def place(self, **kw):
        raise ttk.TclError('Cannot use place with the widget ' + self.__class__.__name__)


class ImageViewer(ttk.Frame):
    def __init__(self, master, path):
        super().__init__(master)
        self.imscale = 1.0  # scale for the canvas image zoom, public for outer classes
        self._delta = 1.3  # zoom magnitude
        self._filter = Image.ANTIALIAS  # could be: NEAREST, BILINEAR, BICUBIC and ANTIALIAS
        self._previous_state = 0  # previous state of the keyboard
        self.path = path

        self.rowconfigure(0, weight=1)  # make the CanvasImage widget expandable
        self.columnconfigure(0, weight=1)
        # Vertical and horizontal scrollbars for canvas
        hbar = AutoScrollbar(self, orient=HORIZONTAL)
        vbar = AutoScrollbar(self, orient=VERTICAL)
        hbar.grid(row=1, column=0, sticky=EW)
        vbar.grid(row=0, column=1, sticky=NS)

        # Create canvas and bind it with scrollbars. Public for outer classes
        self.canvas = ttk.Canvas(self, highlightthickness=0,
                                xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        self.canvas.grid(row=0, column=0, sticky=NSEW)
        self.canvas.update()  # wait till canvas is created
        #hbar.configure(command=self.__scroll_x)  # bind scrollbars to the canvas
        #vbar.configure(command=self.__scroll_y)

        self.canvas.bind('<ButtonPress-1>', self._moveFrom)  # remember canvas position
        self.canvas.bind('<B1-Motion>',     self._moveTo)  # move canvas to the new position

        # Decide if this image huge or not
        self._huge = False  # huge or not
        self._huge_size = 14000  # define size of the huge image
        self._band_width = 1024  # width of the tile band
        Image.MAX_IMAGE_PIXELS = 1000000000  # suppress DecompressionBombError for the big image

        with warnings.catch_warnings():  # suppress DecompressionBombWarning
            warnings.simplefilter('ignore')
            self._image = Image.open(self.path)
            self.imWidth, self.imHeight = self._image.size
            self.imRatio =  self.imWidth /  self.imHeight
        
        self.container = self.canvas.create_rectangle((0, 0, self.imWidth, self.imHeight), width=0)
        self._showImage()  # show image on the canvas
        self.canvas.focus_set()  # set focus on the canvas

    def _showImage(self):
        imageTk = ImageTk.PhotoImage(self._image)
        imageid = self.canvas.create_image(0, 0, anchor=NW, image=imageTk)

        self.canvas.lower(imageid)
        self.canvas.imageTk = imageTk

        box_image = self.canvas.coords(self.container)  # get image area
        box_canvas = (self.canvas.canvasx(0),  # get visible area of the canvas
                      self.canvas.canvasy(0),
                      self.canvas.canvasx(self.canvas.winfo_width()),
                      self.canvas.canvasy(self.canvas.winfo_height()))

        print(box_image)
        print(box_canvas)

    def _moveFrom(self, event:tk.Event):
        """ Remember previous coordinates for scrolling with the mouse """
        self.canvas.scan_mark(event.x, event.y)

    def _moveTo(self, event:tk.Event):
        """ Drag (move) canvas to the new position """
        self.canvas.scan_dragto(event.x, event.y, gain=1)
        self._showImage()  # zoom tile and show it on the canvas

if __name__ == "__main__":
    image = Image.open('assets/nice.jpg')

    imageArr = np.asarray(image)

    app = ttk.Window("Certificates Creation", themename="darkly")
    app.geometry('1600x800')

    imageViwer = ImageViewer(app, 'assets/nice.jpg')
    imageViwer.pack(fill=BOTH, expand=YES)

    app.mainloop()