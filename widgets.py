import math
import time

import warnings

from PIL import Image, ImageTk, ImageSequence
from itertools import cycle
from functools import partial, wraps

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from helperFuncs import containToRange



class ImageLoader(ttk.LabelFrame):
    def __init__(self, master=None, bootstyle=DEFAULT, gifImagePath=None, imagePath=None, zoom=0.5):
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

        if imagePath:
            image = Image.open(imagePath)
            self.loadImage(image)
        else:
            self._startGif()

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


class ImageViewer(ttk.Frame):
    def __init__(self, master=None, imagePath=None, *args, **kwArgs):
        super().__init__(master)

        self.topFrame = ttk.Frame(self)
        self.topFrame.pack(side=TOP, fill=X, pady=5)

        self.imageCanvas = CanvasImage(self, bootstyle=(DEFAULT, ROUND), path=imagePath, *args, **kwArgs)
        self.imageCanvas.pack(side=TOP, expand=YES, fill=BOTH)

        self.xCoordLabel = ttk.Label(self.topFrame, text='X: ')
        self.xCoordLabel.pack(side=LEFT, padx=(0, 3))

        self.xCoordEntry = ttk.Entry(self.topFrame, textvariable=self.imageCanvas.xCoord, width=4, bootstyle=DARK)
        self.xCoordEntry.pack(side=LEFT, padx=(0, 15))

        self.yCoordLabel = ttk.Label(self.topFrame, text='Y: ')
        self.yCoordLabel.pack(side=LEFT, padx=(0, 3))

        self.yCoordEntry = ttk.Entry(self.topFrame, textvariable=self.imageCanvas.yCoord, width=4, bootstyle=DARK)
        self.yCoordEntry.pack(side=LEFT)

    def loadImage(self, path:str):
        self.imageCanvas.loadImage(path)


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


class CanvasImage(ttk.Frame):
    """ Display and zoom image """
    def __init__(self, master=None, bootstyle=DEFAULT, path=None, disableZoomOut=True):
        super().__init__(master)
        """ Initialize the ImageFrame """
        self.imScale = 1.0  # scale for the canvas image zoom, public for outer classes
        self._delta = 1.3  # zoom magnitude
        self._filter = Image.NEAREST  # could be: NEAREST, BILINEAR, BICUBIC and ANTIALIAS
        self._image = None
        self.disableZoomOut = disableZoomOut # allows the image to become smaller than its original size

        # Create ImageFrame in placeholder widget
        # Vertical and horizontal scrollbars for canvas
        self.rowconfigure(0, weight=1)  # make the CanvasImage widget expandable
        self.columnconfigure(0, weight=1)
        hbar = AutoScrollbar(self, bootstyle=bootstyle, orient=HORIZONTAL)
        vbar = AutoScrollbar(self, bootstyle=bootstyle, orient=VERTICAL)
        hbar.grid(row=1, column=0, sticky=EW)
        vbar.grid(row=0, column=1, sticky=NS)

        # Create canvas and bind it with scrollbars. Public for outer classes
        self.canvas = ttk.Canvas(self, highlightthickness=0,
                                xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        self.canvas.grid(row=0, column=0, sticky=NSEW)
        self.canvas.update()  # wait till canvas is created
        hbar.configure(command=self._scrollX)  # bind scrollbars to the canvas
        vbar.configure(command=self._scrollY)

        # Bind events to the Canvas
        self.canvas.bind('<Configure>', lambda _: self._showImage())  # canvas is resized
        self.canvas.bind('<ButtonPress-1>', self._moveFrom)  # remember canvas position
        self.canvas.bind('<B1-Motion>',     self._moveTo)  # move canvas to the new position
        self.canvas.bind('<MouseWheel>', self._wheel)  # zoom for Windows and MacOS, but not Linux
        self.canvas.bind('<Button-5>',   self._wheel)  # zoom for Linux, wheel scroll down
        self.canvas.bind('<Button-4>',   self._wheel)  # zoom for Linux, wheel scroll up
        self.canvas.bind('<Motion>',     self._motion)
        # Handle keystrokes in idle mode, because program slows down on a weak computers,
        # when too many key stroke events in the same time
        self.canvas.bind('<Key>', lambda event: self.canvas.after_idle(self._keystroke, event))

        # Decide if this image huge or not
        self._huge = False  # huge or not
        self._hugeSize = 14000  # define size of the huge image
        self._bandWidth = 1024  # width of the tile band
        Image.MAX_IMAGE_PIXELS = 1000000000  # suppress DecompressionBombError for the big image

        self.xCoord = tk.IntVar(value=0)
        self.yCoord = tk.IntVar(value=0)

        # load image in canvas
        self.loadImage(path)

    def smaller(self):
        """ Resize image proportionally and return smaller image """
        w1, h1 = float(self.imwidth), float(self.imheight)
        w2, h2 = float(self._hugeSize), float(self._hugeSize)
        aspect_ratio1 = w1 / h1
        aspect_ratio2 = w2 / h2  # it equals to 1.0
        if aspect_ratio1 == aspect_ratio2:
            image = Image.new('RGB', (int(w2), int(h2)))
            k = h2 / h1  # compression ratio
            w = int(w2)  # band length
        elif aspect_ratio1 > aspect_ratio2:
            image = Image.new('RGB', (int(w2), int(w2 / aspect_ratio1)))
            k = h2 / w1  # compression ratio
            w = int(w2)  # band length
        else:  # aspect_ratio1 < aspect_ration2
            image = Image.new('RGB', (int(h2 * aspect_ratio1), int(h2)))
            k = h2 / h1  # compression ratio
            w = int(h2 * aspect_ratio1)  # band length
        i, j, n = 0, 1, round(0.5 + self.imheight / self._bandWidth)
        while i < self.imheight:
            print('\rOpening image: {j} from {n}'.format(j=j, n=n), end='')
            band = min(self._bandWidth, self.imheight - i)  # width of the tile band
            self._tile[1][3] = band  # set band width
            self._tile[2] = self._offset + self.imwidth * i * 3  # tile offset (3 bytes per pixel)
            self._image.close()
            self._image = Image.open(self.path)  # reopen / reset image
            self._image.size = (self.imwidth, band)  # set size of the tile band
            self._image.tile = [self._tile]  # set tile
            cropped = self._image.crop((0, 0, self.imwidth, band))  # crop tile band
            image.paste(cropped.resize((w, int(band * k)+1), self._filter), (0, int(i * k)))
            i += band
            j += 1
        print('\r' + 30*' ' + '\r', end='')  # hide printed string
        return image

    def redrawFigures(self):
        """ Dummy function to redraw figures in the children classes """
        pass

    # noinspection PyUnusedLocal
    def _scrollX(self, *args, **kwargs):
        """ Scroll canvas horizontally and redraw the image """
        self.canvas.xview(*args)  # scroll horizontally
        self._showImage()  # redraw the image

    # noinspection PyUnusedLocal
    def _scrollY(self, *args, **kwargs):
        """ Scroll canvas vertically and redraw the image """
        self.canvas.yview(*args)  # scroll vertically
        self._showImage()  # redraw the image

    def _showImage(self):
        """ Show image on the Canvas. Implements correct image zoom almost like in Google Maps """
        box_image = self.canvas.coords(self.container)  # get image area
        box_canvas = (self.canvas.canvasx(0),  # get visible area of the canvas
                      self.canvas.canvasy(0),
                      self.canvas.canvasx(self.canvas.winfo_width()),
                      self.canvas.canvasy(self.canvas.winfo_height()))

        box_img_int = tuple(map(int, box_image))  # convert to integer or it will not work properly
        # Get scroll region box
        box_scroll = [min(box_img_int[0], box_canvas[0]), min(box_img_int[1], box_canvas[1]),
                      max(box_img_int[2], box_canvas[2]), max(box_img_int[3], box_canvas[3])]

        # Horizontal part of the image is in the visible area
        if  box_scroll[0] == box_canvas[0] and box_scroll[2] == box_canvas[2]:
            box_scroll[0]  = box_img_int[0]
            box_scroll[2]  = box_img_int[2]
        # Vertical part of the image is in the visible area
        if  box_scroll[1] == box_canvas[1] and box_scroll[3] == box_canvas[3]:
            box_scroll[1]  = box_img_int[1]
            box_scroll[3]  = box_img_int[3]

        # Convert scroll region to tuple and to integer
        self.canvas.configure(scrollregion=tuple(map(int, box_scroll)))  # set scroll region

        x1 = max(box_canvas[0] - box_image[0], 0)  # get coordinates (x1,y1,x2,y2) of the image tile
        y1 = max(box_canvas[1] - box_image[1], 0)
        x2 = min(box_canvas[2], box_image[2]) - box_image[0]
        y2 = min(box_canvas[3], box_image[3]) - box_image[1]

        if int(x2 - x1) > 0 and int(y2 - y1) > 0:  # show image if it in the visible area
            if self._huge and self._currImg < 0:  # show huge image
                h = int((y2 - y1) / self.imScale)  # height of the tile band
                self._tile[1][3] = h  # set the tile band height
                self._tile[2] = self._offset + self.imwidth * int(y1 / self.imScale) * 3
                self._image.close()
                self._image = Image.open(self.path)  # reopen / reset image
                self._image.size = (self.imwidth, h)  # set size of the tile band
                self._image.tile = [self._tile]
                image = self._image.crop((int(x1 / self.imScale), 0, int(x2 / self.imScale), h))
            else:  # show normal image
                image = self._pyramid[max(0, self._currImg)].crop(  # crop current img from pyramid
                                    (int(x1 / self._scale), int(y1 / self._scale),
                                     int(x2 / self._scale), int(y2 / self._scale)))
            imagetk = ImageTk.PhotoImage(image.resize((int(x2 - x1), int(y2 - y1)), self._filter))

            imageid = self.canvas.create_image(max(box_canvas[0], box_img_int[0]),
                                               max(box_canvas[1], box_img_int[1]),
                                               anchor=NW, image=imagetk)
            self.canvas.lower(imageid)  # set image into background
            self.canvas.imagetk = imagetk  # keep an extra reference to prevent garbage-collection

            # set current center value
            # check if image fills the x-axis of the canvas
            if self.canvas.canvasx(self.canvas.winfo_width()) > int(x2 - x1):
                self._imageCoversXaxis = FALSE
                self._currCenter[0] = self.canvas.canvasx(0) - box_scroll[0]
            else:
                self._imageCoversXaxis = TRUE
                self._currCenter[0] = (int(x1 / self._scale))

            # check if image fills the y-axis of the canvas
            if self.canvas.canvasy(self.canvas.winfo_height()) > int(y2 - y1):
                self._imageCoversYaxis = FALSE
                self._currCenter[1] = self.canvas.canvasy(0) - box_scroll[1]
            else:
                self._imageCoversYaxis = TRUE
                self._currCenter[1] = int(y1 / self._scale)

    def _moveFrom(self, event:tk.Event):
        """ Remember previous coordinates for scrolling with the mouse """
        self.lastPos = (event.x, event.y)
        self.canvas.scan_mark(event.x, event.y)

    def _moveTo(self, event:tk.Event):
        """ Drag (move) canvas to the new position """
        self.canvas.scan_dragto(event.x, event.y, gain=1)
        self._showImage()  # zoom tile and show it on the canvas

    def _outside(self, x, y):
        """ Checks if the point (x,y) is outside the image area """
        bbox = self.canvas.coords(self.container)  # get image area
        if bbox[0] < x < bbox[2] and bbox[1] < y < bbox[3]:
            return False  # point (x,y) is inside the image area
        else:
            return True  # point (x,y) is outside the image area

    def _wheel(self, event:tk.Event):
        """ Zoom with mouse wheel """
        x = self.canvas.canvasx(event.x)  # get coordinates of the event on the canvas
        y = self.canvas.canvasy(event.y)
        if self._outside(x, y): return  # zoom only inside image area
        scale = 1.0
        # Respond to Linux (event.num) or Windows (event.delta) wheel event
        if event.num == 5 or event.delta == -120:  # scroll down, smaller
            newImScale = self.imScale / self._delta
            if self.disableZoomOut and newImScale < 1: # allow the image to become smaller than its normal size
                return
            if round(self._minSide * self.imScale) < 30: return  # image is less than 30 pixels
            self.imScale  = newImScale
            scale        /= self._delta
        if event.num == 4 or event.delta == 120:  # scroll up, bigger
            i = min(self.canvas.winfo_width(), self.canvas.winfo_height()) >> 1
            if i < self.imScale: return  # 1 pixel is bigger than the visible area
            self.imScale *= self._delta
            scale        *= self._delta
        # Take appropriate image from the pyramid
        k = self.imScale * self._ratio  # temporary coefficient
        self._currImg = min((-1) * int(math.log(k, self._reduction)), len(self._pyramid) - 1)
        self._scale = k * math.pow(self._reduction, max(0, self._currImg))
        #
        self.canvas.scale(ALL, x, y, scale, scale)  # rescale all objects
        # Redraw some figures before showing image on the screen
        self.redrawFigures()  # method for child classes
        self._showImage()

    def _keystroke(self, event:tk.Event):
        """ Scrolling with the keyboard.
            Independent from the language of the keyboard, CapsLock, <Ctrl>+<key>, etc. """
        if event.state - self._previous_state == 4:  # means that the Control key is pressed
            pass  # do nothing if Control key is pressed
        else:
            self._previous_state = event.state  # remember the last keystroke state
            # Up, Down, Left, Right keystrokes
            if event.keycode in [68, 39, 102]:  # scroll right: keys 'D', 'Right' or 'Numpad-6'
                self._scrollX('scroll',  1, 'unit', event=event)
            elif event.keycode in [65, 37, 100]:  # scroll left: keys 'A', 'Left' or 'Numpad-4'
                self._scrollX('scroll', -1, 'unit', event=event)
            elif event.keycode in [87, 38, 104]:  # scroll up: keys 'W', 'Up' or 'Numpad-8'
                self._scrollY('scroll', -1, 'unit', event=event)
            elif event.keycode in [83, 40, 98]:  # scroll down: keys 'S', 'Down' or 'Numpad-2'
                self._scrollY('scroll',  1, 'unit', event=event)

    def _canvasCoordsToImageCoords(self, x, y):
        if self._imageCoversXaxis:
            xCoord = int(self._currCenter[0] + (x / self.imScale))
        else:
            xCoord = int((self._currCenter[0] + x) / self.imScale)

        if self._imageCoversYaxis:
            yCoord = int(self._currCenter[1] + (y / self.imScale))
        else:
            yCoord = int((self._currCenter[1] + y) / self.imScale)

        return (xCoord, yCoord)

    def _motion(self, event:tk.Event):
        x = self.canvas.canvasx(event.x)  # get coordinates of the event on the canvas
        y = self.canvas.canvasy(event.y)

        if self._outside(x, y): return

        temp = self._canvasCoordsToImageCoords(event.x, event.y)
        self.xCoord.set(temp[0])
        self.yCoord.set(temp[1])

    def crop(self, bbox):
        """ Crop rectangle from the image and return it """
        if self._huge:  # image is huge and not totally in RAM
            band = bbox[3] - bbox[1]  # width of the tile band
            self._tile[1][3] = band  # set the tile height
            self._tile[2] = self._offset + self.imwidth * bbox[1] * 3  # set offset of the band
            self._image.close()
            self._image = Image.open(self.path)  # reopen / reset image
            self._image.size = (self.imwidth, band)  # set size of the tile band
            self._image.tile = [self._tile]
            return self._image.crop((bbox[0], 0, bbox[2], band))
        else:  # image is totally in RAM
            return self._pyramid[0].crop(bbox)

    def loadImage(self, path:str):
        # TODO when the new image loaded is smalled than the current one, the scrollbox
        # is out of bounds
        if self._image is not None:
            self._image.close()
            self.canvas.delete(self.container)
            map(lambda i: i.close, self._pyramid)  # close all pyramid images

        self._previous_state = 0  # previous state of the keyboard
        self.path = path  # path to the image, should be public for outer classes

        self._currCenter = [0, 0]  # coordinate center
        self._imageCoversXaxis = FALSE
        self._imageCoversYaxis = FALSE

        with warnings.catch_warnings():  # suppress DecompressionBombWarning
            warnings.simplefilter('ignore')
            self._image = Image.open(self.path)  # open image, but down't load it
        self.imwidth, self.imheight = self._image.size  # public for outer classes

        if self.imwidth * self.imheight > self._hugeSize * self._hugeSize and \
           self._image.tile[0][0] == 'raw':  # only raw images could be tiled
            self._huge = True  # image is huge
            self._offset = self._image.tile[0][2]  # initial tile offset
            self._tile = [self._image.tile[0][0],  # it have to be 'raw'
                           [0, 0, self.imwidth, 0],  # tile extent (a rectangle)
                           self._offset,
                           self._image.tile[0][3]]  # list of arguments to the decoder
        self._minSide = min(self.imwidth, self.imheight)  # get the smaller image side
        # Create image pyramid
        self._pyramid = [self.smaller()] if self._huge else [Image.open(self.path)]
        # Set ratio coefficient for image pyramid
        self._ratio = max(self.imwidth, self.imheight) / self._hugeSize if self._huge else 1.0
        self._currImg = 0  # current image from the pyramid
        self._scale = self.imScale * self._ratio  # image pyramide scale
        self._reduction = 2  # reduction degree of image pyramid
        w, h = self._pyramid[-1].size
        while w > 512 and h > 512:  # top pyramid image is around 512 pixels in size
            w /= self._reduction  # divide on reduction degree
            h /= self._reduction  # divide on reduction degree
            self._pyramid.append(self._pyramid[-1].resize((int(w), int(h)), self._filter))
        # Put image into container rectangle and use it to set proper coordinates to the image
        self.container = self.canvas.create_rectangle((0, 0, self.imwidth, self.imheight), width=0)

        self.canvas.scan_dragto(0, 0, gain=1)
        self._showImage()  # zoom tile and show it on the canvas
        self.canvas.focus_set()  # set focus on the canvas

    def destroy(self):
        """ ImageFrame destructor """
        self._image.close()
        map(lambda i: i.close, self._pyramid)  # close all pyramid images
        del self._pyramid[:]  # delete pyramid list
        del self._pyramid  # delete pyramid variable
        self.canvas.destroy()
        self.destroy()


class ColorChooser(ttk.Frame):
    def __init__(self, master=None, defaultColor:tuple = (75, 75, 75)):
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
        return self.fromRGB(colorRGBTuple)

    @staticmethod
    def fromRGB(rgb):
        """translates an rgb tuple of int to a tkinter friendly color code"""
        r, g, b = rgb
        return f'#{r:02x}{g:02x}{b:02x}'

    def keysPressed(topWidget, entryTextVar, event:tk.Event):
        minValue = 0
        maxValue = 255

        if event.keysym == 'Right':
            # check if the cursor is in the end of the word
            # (don't want to fire the event if the user just wants
            # to move the cursor)
            if event.widget.index(INSERT) == len(str(entryTextVar.get())):
                value = entryTextVar.get() + 1
                if value <= maxValue:
                    entryTextVar.set(value)
        elif event.keysym == 'Left':
            # check if the cursor is at the start of the word
            # (don't want to fire the event if the user just wants
            # to move the cursor)
            if event.widget.index(INSERT) == 0:
                value = entryTextVar.get() - 1
                if value >= minValue:
                    entryTextVar.set(value)


class DataViewer(ttk.Frame):
    """A custom 2D Ttk Treeview widget that displays a hierarchical collection of items.

    Each item has a textual label and an optional list of data values.
    The data values are displayed in successive columns
    after the tree label. Entries have 2 values, name and email.

    The treeview supports 3 types of entries:

    1. Entries without a 'flaggedEmail' or 'flaggedName' tag\n
    2. Entries with a 'flaggedEmail' tag\n
    3. Entries with a 'flaggedName' tag\n

    Each type of entry has a distinct background color.
    Entries are grouped together based on their tag and each group
    is shown in the order thats specified above."""

    def __init__(
        self,
        master=None,
        bootstyle=DEFAULT,
        *args,
        **kwargs,
    ):
        """Construct a Ttk Treeview with parent master.

        STANDARD OPTIONS

            class, cursor, style, takefocus, xscrollcommand,
            yscrollcommand

        WIDGET-SPECIFIC OPTIONS

            columns, displaycolumns, height, padding, selectmode, show

        ITEM OPTIONS

            text, values, open, tags

        TAG OPTIONS

            foreground, background, font, image
        """
        super().__init__(master)

        # make tree resizable
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        # define columns
        self._columns = ('index', 'name', 'email')
        # internal var, used in adding the appropriate index to each tree entry
        self._currIndex = 1
        # used to track where the next valid item (without a tag) should be inserted
        self._currValidIndex = 0
        # stacks that stores edits. (used in undo and redo)
        self.editStack = []
        # stack size
        self.stackSize = 25
        # stack index that points to the current edit
        self.stackIndex = -1
        # true if we are editing a row
        self._editMode = False
        self._itemToEdit = None

        self._tree = ttk.Treeview(
            self,
            bootstyle=bootstyle,
            columns=self._columns,
            show=HEADINGS,
            *args,
            **kwargs)
        self._tree.grid(row=0, column=0, sticky=NSEW)

        self._tree.tag_configure('flaggedEmail', background='#CA9242', foreground='white')
        self._tree.tag_configure('flaggedName', background='#ca5f42', foreground='white')

        # define and tweak columns
        self._tree.column("# 1", stretch=NO, width=45)
        self._tree.heading('index', text='Index')
        self._tree.heading('name', text='Name')
        self._tree.heading('email', text='Email')

        # setup scrollbar
        self.scrollbar = AutoScrollbar(
            self,
            orient=VERTICAL,
            command=self._tree.yview)

        self._tree.configure(yscroll=self.scrollbar.set)
        self.scrollbar.grid(row=0, column=1, sticky=NS)

        self._editName = ttk.StringVar()
        self._editEmail = ttk.StringVar()

        self._editFrame = ttk.Frame(self._tree)
        self._editFrame.columnconfigure(0, weight=1)
        self._editFrame.columnconfigure(1, weight=1)

        self._editNameEntry = ttk.Entry(self._editFrame, textvariable=self._editName)
        self._editNameEntry.grid(row=0, column=0, sticky=EW)

        self._editEmailEntry = ttk.Entry(self._editFrame, textvariable=self._editEmail)
        self._editEmailEntry.grid(row=0, column=1, sticky=EW)

        self._tree.bind('<<TreeviewSelect>>', self._itemSelected, add='+')
        self._tree.bind('<Double-Button-1>', self._enterEditMode, add='+')
        self.bind_all('<space>', self._createEntry, add='+')
        self.bind_all('<Escape>', self._cancelEditMode, add='+')
        self.bind_all('<Return>', self._leaveEditMode, add='+')
        self.bind_all('<Button-3>', self._leaveEditMode, add='+')
        self.bind_all('<Delete>', self._deleteSelectedEntry, add='+')
        self.bind_all('<Control-z>', self._undo, add='+')

    def notOnEditMode(func):
        @wraps(func)
        def wrapperFunc(self, *args, **kwargs):
            if not self._editMode:
                func(self, *args, **kwargs)
        return wrapperFunc

    def loadList(self, itemList:list):
        for item in itemList:
            self.insertEntry(item, saveEdit=False)

        self._recalculateIndexes()
        # select top entry
        self._clearTreeviewSelection()
        self._tree.selection_add(self._tree.get_children()[0])

    @notOnEditMode
    def insertEntry(
        self,
        values:list,
        tags:tuple=None,
        index:int=END,
        focus:bool=False,
        saveEdit=True
        ):
        """insert an item.

        POSSIBLE TAGS

        flaggedEmail, flaggedName
        """
        # add items index to items values
        values.insert(0, self._currIndex)
        self._currIndex += 1

        if tags is not None:
            item = self._tree.insert('', index, values=values, tags=tags)
        else:
            self._currValidIndex += 1
            item = self._tree.insert('', index, values=values)

        if saveEdit:
            self._pushEdit(('insert', item))

        if focus:
            # select entry
            self._clearTreeviewSelection()
            self._tree.selection_add(item)

    def _createEntry(self, event:tk.Event=None):
        """create a new treeview entry and add it just before the
        entries with a tag"""
        self.insertEntry(['', ''], index=self._currValidIndex, focus=True)
        self._recalculateIndexes()

    def _deleteSelectedEntry(self, event:tk.Event=None):
        try:
            entryToDelete = self._tree.selection()[0]
        except:
            return
        self._deleteEntry(entryToDelete)

    @notOnEditMode
    def _deleteEntry(self, entry, saveEdit=True):
        # get item index in the tree
        itemIndex = int(self._tree.item(entry, 'values')[0]) - 1

        if self._tree.item(entry, 'tags') == '':
            self._currValidIndex -= 1

        if saveEdit:
            self._pushEdit(('delete', self._tree.item(entry), itemIndex))

        self._tree.delete(entry)
        self._recalculateIndexes()

        # select the item with the same index as the one we deleted
        # ex. if we deleted item with index 42 select the new item with
        # index 42
        items = self._tree.get_children()
        numOfItems = len(items)

        if numOfItems == 0:
            return
        elif numOfItems == itemIndex:
            itemIndex -= 1

        temp = self._tree.get_children()[itemIndex]
        self._tree.selection_add(temp)

    def _itemSelected(self, event:tk.Event=None):
        pass

    def _enterEditMode(self, event:tk.Event=None):
        self._editMode = True
        self._itemToEdit = self._tree.selection()[0]
        user = self._tree.item(self._itemToEdit)['values']
        self._editName.set(user[1])
        self._editEmail.set(user[2])
        self._editFrame.place(relwidth=0.9, anchor=CENTER, relx=0.5, rely=0.5)

    def _leaveEditMode(self, event:tk.Event=None):
        """Save changes and leave edit mode"""
        if not self._editMode: return
        newValues = (self._editName.get(), self._editEmail.get())
        self._editEntryValues(self._itemToEdit, newValues)
        self._editMode = False
        self._editFrame.place_forget()

    def _editEntryValues(self, item, values:tuple, saveEdit=True):
        oldValues = self._tree.item(item, 'values')
        if saveEdit:
            self._pushEdit(('edit', item, oldValues))
        newItemValues = (oldValues[0], values[0], values[1])
        self._tree.item(item, values=newItemValues)

    def _cancelEditMode(self, event:tk.Event=None):
        """Leave edit mode without saving the changes"""
        if self._editMode:
            self._editMode = False
            self._editFrame.place_forget()

    @notOnEditMode
    def _undo(self, event:tk.Event=None):
        """undo the latest edit"""
        if self.stackIndex < 0:
            return

        edit = self.editStack[self.stackIndex]
        if edit[0] == 'insert':
            self._deleteEntry(edit[1], saveEdit=False)
        elif edit[0] == 'delete':
            values = edit[1]['values']
            values.pop(0)  # remove entry index
            tags = edit[1]['tags']
            self.insertEntry(values=values, tags=tags,
                index=edit[2], saveEdit=False)
            if edit[1]['tags'] == '':
                self._currValidIndex += 1
        elif edit[0] == 'edit':
            values = list(edit[2])
            values.pop(0)
            self._editEntryValues(edit[1], values, saveEdit=False)
        self.stackIndex -= 1

    @notOnEditMode
    def _redo(self):
        """redo the latest edit"""
        if self.stackIndex == self.stackSize - 1:
            return

        self.stackIndex += 1
        edit = self.editStack[self.stackIndex]
        if edit[0] == 'insert':
            self._deleteEntry(edit[1], saveEdit=False)
        elif edit[0] == 'delete':
            values = edit[1]['values']
            values.pop(0)  # remove entry index
            tags = edit[1]['tags']
            self.insertEntry(values=values, tags=tags,
                index=edit[2], saveEdit=False)
            if edit[1]['tags'] == '':
                self._currValidIndex += 1
        elif edit[0] == 'edit':
            values = list(edit[2])
            values.pop(0)
            self._editEntryValues(edit[1], values, saveEdit=False)
        self.stackIndex -= 1

    def _pushEdit(self, edit):
        self.editStack.insert(self.stackIndex + 1, edit)
        if self.stackSize < len(self.editStack):
            self._deleteOldestEdit()
        else:
            self.stackIndex += 1

    def _deleteOldestEdit(self):
        if self.stackSize - (self.stackIndex + 1) >=\
            (self.stackIndex + 1):
            del self.editStack[-1]
            # update editStack index
            self.stackIndex += 1
        elif self.stackSize - (self.stackIndex + 1) <\
            (self.stackIndex + 1):
            del self.editStack[0]

    def _recalculateIndexes(self):
        for index, item in enumerate(self._tree.get_children()):
            newItemvalues = self._tree.item(item)['values']
            newItemvalues[0] = index + 1
            self._tree.item(item, values=newItemvalues)

    def _clearTreeviewSelection(self):
        for i in self._tree.selection():
            self._tree.selection_remove(i)

    def _reset(self):
        items = self._tree.get_children()

        if len(items) != 0:
            self._tree.delete(*items)
        self._currIndex = 1
        self._currValidIndex = 0
        self.editStack = []
        self._cancelEditMode()


class EmailCreator(ttk.Frame):
    def __init__(self, master=None, *args, **kwargs):
        super().__init__(master, padding=10)

        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)

        # Default behavior is batch sending of emails.
        # Disables batch sending and enables the sending
        # of personal emails (with a single recipient).
        self.personalEmail = False
        self.emailSignature = ''

        self._title = EntryWithPlaceholder(self, placeholder='Title')
        self._title.grid(row=0,  column=0, sticky=EW, pady=(0, 5))

        self._receiver = EntryWithPlaceholder(self, placeholder='Recipient')

        self._body = ttk.Text(self, *args, **kwargs)
        self._body.grid(row=2,  column=0, sticky=NSEW, pady=(5, 0))

        self._body.bind('<KeyPress-t>', self.getEmail)

    def enablePersonalEmails(self):
        self.personalEmail = True
        self._receiver.grid(row=1,  column=0, sticky=EW, pady=(5,5))

    def disablePersonalEmails(self):
        self.personalEmail = False
        self._receiver.grid_remove()

    def getEmail(self, _):
        """returns the email info in a form of a dict.
        Email info consists of the title, the recipient and the body of
        the email in HTML form. If the personalEmail flag is false, the
        recipient is empty.

        Returns:
            dict: email info
        """
        email = {}
        email['title'] = self._title.get()

        recipient = ''
        if self.personalEmail:
            recipient = self._receiver.get()
        email['recipient'] = recipient

        signature = self.getSignature()
        body = self._body.get('1.0', END)
        body = body.replace('\n', '<br>')
        body = '<html><head></head><body><p style="color:black">' + body +\
        signature + '</p></body></html>'

        email['body'] = body
        return email

    def getSignature(self):
        with open('emailSignature.html', 'r') as file:
            signature = file.read()
        return signature


class EntryWithPlaceholder(ttk.Entry):
    def __init__(self, master=None, placeholder='placeholder', placeholderColor='gray', *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.placeholder = placeholder
        self.placeholderColor = placeholderColor
        self.defaultFgColor = self['foreground']

        self.bind("<FocusIn>", self.focusIn)
        self.bind("<FocusOut>", self.focusOut)

        self.putPlaceholder()

    def putPlaceholder(self):
        self.insert(0, self.placeholder)
        self['foreground'] = self.placeholderColor

    def focusIn(self, _):
        if str(self['foreground']) == self.placeholderColor:
            self.delete('0', END)
            self['foreground'] = self.defaultFgColor

    def focusOut(self, _):
        if not self.get():
            self.putPlaceholder()


class tkEntryWithPlaceholder(tk.Entry):
    def __init__(self, master=None, placeholder='placeholder', placeholderColor='gray', *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.placeholder = placeholder
        self.placeholderColor = placeholderColor
        self.defaultFgColor = self['foreground']

        self.bind("<FocusIn>", self.focusIn)
        self.bind("<FocusOut>", self.focusOut)

        self.putPlaceholder()

    def putPlaceholder(self):
        self.insert(0, self.placeholder)
        self['foreground'] = self.placeholderColor

    def focusIn(self, _):
        if str(self['foreground']) == self.placeholderColor:
            self.delete('0', END)
            self['foreground'] = self.defaultFgColor

    def focusOut(self, _):
        if not self.get():
            self.putPlaceholder()


class TextEditor(ttk.Frame):

    def __init__(
        self,
        master,
        padding=0,
        bootstyle=DEFAULT,
        vbar=True,
        hbar=False,
        **kwargs,
    ):
        super().__init__(master, padding=padding)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        darkColor = '#303030'
        secondaryColor = '#444444'
        numFontColor = '#687273'
        textFontColor = '#e8e8e8'
        cursorColor = '#f7d4d4'
        darkBackgroundColor = '#222222'
        selectedBackgroundColor = '#444444'
        selectedForegroundColor = '#f7d4d4'
        findBackground = '#2b2b2b'
        lighterDarkBackgroundColor= '#363636'

        font = ('Arial', '14')
        findFont = ('Arial', '13')
        self._lastLineIndex = 0  # stores the row index of the previously selected line

        # setup text widget
        self._numberedText = NumberedText(
            master=self,
            wrap=NONE,
            autostyle=False,
            font=font,
            borderwidth=0,
            highlightthickness=0,
            foreground=numFontColor,
            background=darkColor)

        self._text = CText(
            master=self,
            wrap=NONE,
            undo=True,
            maxundo=-1,
            autoseparators=True,
            autostyle=False,
            font=font,
            insertwidth=3,
            borderwidth=0,
            highlightthickness=0,
            background=darkColor,
            foreground=textFontColor,
            insertbackground=cursorColor,
            selectbackground=secondaryColor,
            **kwargs)

        self._numberedText.tag_configure('tag_selected', foreground=selectedForegroundColor)
        self._text.tag_configure('tag_selected', background=selectedBackgroundColor)
        self._text.tag_configure('tag_found', background=selectedBackgroundColor)

        self._hbar = None
        self._vbar = None

        # delegate text methods to frame
        for method in vars(ttk.Text).keys():
            if any(['pack' in method, 'grid' in method, 'place' in method]):
                pass
            else:
                setattr(self, method, getattr(self._text, method))

        # setup scrollbars
        if vbar is not None:
            self._vbar = AutoScrollbar(
                master=self,
                bootstyle=bootstyle,
                command=self._scrollBoth,
                orient=VERTICAL,
            )
            self._vbar.grid(row=0, rowspan=2, column=2, sticky=NS)
            self._numberedText.configure(yscrollcommand=self._updateScroll)
            self._text.configure(yscrollcommand=self._updateScroll)

        if hbar is not None:
            self._hbar = AutoScrollbar(
                master=self,
                bootstyle=bootstyle,
                command=self._text.xview,
                orient=HORIZONTAL,
            )
            self._hbar.grid(row=1, column=0, columnspan=2, sticky=EW)
            self._text.configure(xscrollcommand=self._hbar.set)

        self._text.bind('<<TextChanged>>', self._onChange)

        self._numberedText.grid(row=0, column=0, sticky=NS)
        self._text.grid(row=0, column=1, sticky=NSEW)

        # setup search functionality

        self._isSearchOpen = False
        self._findText = ttk.StringVar(self)
        self._findFrame = ttk.Frame(self._text)

        self._findEntry = tkEntryWithPlaceholder(
            self._findFrame,
            placeholder='Find..',
            autostyle=False,
            font=findFont,
            borderwidth=0,
            insertwidth=2,
            highlightthickness=0,
            background=findBackground,
            foreground=textFontColor,
            insertbackground=cursorColor,
            textvariable=self._findText)
        self._findEntry.pack(side=LEFT, pady=2, padx=(10, 4))

        #Import the image using PhotoImage function
        self._findButtonImg= ttk.PhotoImage(file='assets/x1.png')

        self._findCloseButton = tk.Button(
            self._findFrame,
            autostyle=False,
            image=self._findButtonImg,
            borderwidth=0,
            highlightthickness=0,
            background=darkBackgroundColor,
            activebackground=lighterDarkBackgroundColor,
            relief=FLAT,
            command=self._closeSearch)
        self._findCloseButton.pack(side=LEFT, expand=NO, pady=2, padx=(0, 4))

        self._text.bind_all('<Control-KeyPress-f>', lambda e: self._openSearch(), add='+')
        self._text.bind_all('<Escape>', lambda e: self._closeSearch(), add='+')

    def loadFile(self, path:str):
        self.reset()
        with open(path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for row in lines:
                self._text.insert(END, row)

    def _openSearch(self):
        self._findFrame.place(relx=0.98, rely=0, anchor=NE, bordermode=OUTSIDE)
        self._isSearchOpen = True

    def _closeSearch(self):
        self._findFrame.place_forget()
        self._isSearchOpen = False

    def reset(self):
        # remove selected background from the last selected line
        self._numberedText.tag_remove('tag_selected', f'{self._lastLineIndex}.0', f'{self._lastLineIndex}.end')
        self._text.tag_remove('tag_selected', f'{self._lastLineIndex}.0', f'{self._lastLineIndex}.0+1lines')
        self._lastLineIndex = 0
        # clean text
        self._text.delete('1.0', END)

    def _onChange(self, *_):
        newNumOfLines = self._text.count('1.0', END, 'displaylines')[0]
        self._numberedText.setNumOfLines(newNumOfLines)

        # remove selected background from the last selected line
        self._numberedText.tag_remove('tag_selected', f'{self._lastLineIndex}.0', f'{self._lastLineIndex}.end')
        self._text.tag_remove('tag_selected', f'{self._lastLineIndex}.0', f'{self._lastLineIndex}.0+1lines')
        # get current line row index
        curRow = self._text.index('insert').split('.')[0]
        self._lastLineIndex = curRow
        # set background of currently selected line
        self._numberedText.tag_add('tag_selected', f'{curRow}.0', f'{curRow}.0+1lines')
        self._text.tag_add('tag_selected', f'{curRow}.0', f'{curRow}.0+1lines')

    def _scrollBoth(self, action, position):
        self._text.yview_moveto(position)
        self._numberedText.yview_moveto(position)

    def _updateScroll(self, first, last):
        self._text.yview_moveto(first)
        self._numberedText.yview_moveto(first)
        self._vbar.set(first, last)


class CText(tk.Text):
    """Text widget which generates an event '<<TextChanged>>' whenever
    the text is modified or the view is changed.

    STANDARD OPTIONS

        background, borderwidth, cursor,
        exportselection, font, foreground,
        highlightbackground, highlightcolor,
        highlightthickness, insertbackground,
        insertborderwidth, insertofftime,
        insertontime, insertwidth, padx, pady,
        relief, selectbackground,
        selectborderwidth, selectforeground,
        setgrid, takefocus,
        xscrollcommand, yscrollcommand,

    WIDGET-SPECIFIC OPTIONS

        autoseparators, height, maxundo,
        spacing1, spacing2, spacing3,
        state, tabs, undo, width, wrap,

    WIDGET-SPECIFIC EVENTS

        <<TextChanged>>
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # create a proxy for the underlying widget
        # self._w is the name of the widget (cText)
        # each time an event happens it is passed to a tcl command which has
        # the same name as the widget class (cText)

        # rename the main tcl command (cText) to cText_orig
        # !!!ATTENTION!!!
        # we don't rename the var self._w, but the command thats named after self._w
        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        # after that, create a proxy command and give it the same name as the one
        # of the old command (cText), so that, when an event happens, the new proxy
        # func is called.
        self.tk.createcommand(self._w, self._proxy)

    def _proxy(self, *args):
        # pass the args to the original widget function
        result = None
        try:
            cmd = (self._orig,) + args
            result = self.tk.call(cmd)
        except tk.TclError:
            print(f'_tkinter.TclError. Command args: {args}')

        # generate an event if something was added or deleted,
        # or the cursor position changed
        if (args[0] in ("insert", "replace", "delete") or
            args[0:3] == ("mark", "set", "insert") or
            args[0:2] == ("xview", "moveto") or
            args[0:2] == ("xview", "scroll") or
            args[0:2] == ("yview", "moveto") or
            args[0:2] == ("yview", "scroll")
        ):
            self.event_generate("<<TextChanged>>", when="tail")

        # return what the actual widget returned
        return result


class NumberedText(tk.Text):
    """Text widget where each line is a number. Numbers are
    sorted in ascending order.

    STANDARD OPTIONS

        background, borderwidth, cursor,
        exportselection, font, foreground,
        highlightbackground, highlightcolor,
        highlightthickness, insertbackground,
        insertborderwidth, insertofftime,
        insertontime, insertwidth, padx, pady,
        relief, selectbackground,
        selectborderwidth, selectforeground,
        setgrid, takefocus,
        xscrollcommand, yscrollcommand,

    WIDGET-SPECIFIC OPTIONS

        autoseparators, height, maxundo,
        spacing1, spacing2, spacing3,
        state, tabs, undo, width, wrap,
    """

    def __init__(self, width=5, *args, **kwargs):
        super().__init__(width=width, state=DISABLED, *args, **kwargs)
        # move every index to the right of the line
        self.tag_configure('tag_right', justify=RIGHT)
        self._numOfLines = 0

    def setNumOfLines(self, newNumOfLines):
        if self._numOfLines != newNumOfLines:
            self._numOfLines = newNumOfLines
            self._recalculateNumbers()

    def _recalculateNumbers(self):
        self.configure(state=NORMAL)
        # clear all indexes
        self.delete('1.0', END)
        # recalculate all line indexes
        for i in range(self._numOfLines):
            self.insert(END, f'{i + 1}  \n', 'tag_right')

        # remove empty line thats constanlty added by the text widget
        if self.get('end-1c', END) == '\n':
            self.delete('end-1c', END)
        self.configure(state=DISABLED)

DEBUG = 'debug'
INFO = 'info'
WARNING = 'warning'
ERROR = 'error'
SUCCESS = 'success'


class Logger(ttk.Frame):
    """Logger widget used to display custom logs and errors."""
    def __init__(
        self,
        master,
        padding=0,
        timestamp=True,
        logLevel=1,
        bootstyle=DEFAULT,
        vbar=True,
        hbar=False,
        **kwargs,
    ):
        """Contract a Logger widget with a parent master.

        STANDARD OPTIONS

        timestamp: If true every log will have a timestamp
        logLevel: the minimum level of logLevel to be displayed

        0 = DEBUG, 1 = INFO, 2=WARNING, 3=ERROR/SUCCESS

        0 should never be used on a live version
        """
        super().__init__(master, padding=padding)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        timestampColor = 'white'
        infoColor = '#ADB5BD'
        warningColor = '#f39c12'
        errorColor = '#e74c3c'
        SuccessColor  = '#00bc8c'


        darkColor = '#303030'
        secondaryColor = '#444444'
        numFontColor = '#687273'
        textFontColor = '#e8e8e8'
        cursorColor = '#f7d4d4'
        darkBackgroundColor = '#222222'
        selectedBackgroundColor = '#444444'
        selectedForegroundColor = '#f7d4d4'
        findBackground = '#2b2b2b'
        lighterDarkBackgroundColor= '#363636'

        font = ('Arial', '14')
        findFont = ('Arial', '13')

        self._lastLineIndex = 0  # stores the row index of the previously selected line
        self.logLevel = logLevel  # store logLevel as a public var
        self._timestamp = timestamp

        self._text = CText(
            master=self,
            state=DISABLED,
            wrap=NONE,
            undo=True,
            maxundo=-1,
            autoseparators=True,
            autostyle=False,
            font=font,
            insertwidth=3,
            borderwidth=0,
            highlightthickness=0,
            background=darkColor,
            foreground=textFontColor,
            insertbackground=cursorColor,
            selectbackground=secondaryColor,
            **kwargs)

        self._text.tag_configure('timestamp_tag', foreground=timestampColor)
        self._text.tag_configure('tag_selected', foreground=selectedBackgroundColor)
        self._text.tag_configure('tag_found', foreground=selectedBackgroundColor)

        self._text.tag_configure('tag_debug', foreground=infoColor)
        self._text.tag_configure('tag_info', foreground=infoColor)
        self._text.tag_configure('tag_warning', foreground=warningColor)
        self._text.tag_configure('tag_error', foreground=errorColor)
        self._text.tag_configure('tag_success', foreground=SuccessColor)

        self._hbar = None
        self._vbar = None

        # delegate text methods to frame
        for method in vars(ttk.Text).keys():
            if any(['pack' in method, 'grid' in method, 'place' in method]):
                pass
            else:
                setattr(self, method, getattr(self._text, method))

        # setup scrollbars
        if vbar is not None:
            self._vbar = AutoScrollbar(
                master=self,
                bootstyle=bootstyle,
                command=self._text.yview,
                orient=VERTICAL,
            )
            self._vbar.grid(row=0, rowspan=2, column=2, sticky=NS)
            self._text.configure(yscrollcommand=self._vbar.set)

        if hbar is not None:
            self._hbar = AutoScrollbar(
                master=self,
                bootstyle=bootstyle,
                command=self._text.xview,
                orient=HORIZONTAL,
            )
            self._hbar.grid(row=1, column=0, columnspan=2, sticky=EW)
            self._text.configure(xscrollcommand=self._hbar.set)

        self._text.bind('<<TextChanged>>', self._onChange)

        self._text.grid(row=0, column=1, sticky=NSEW)

        # setup search functionality
        self._isSearchOpen = False
        self._findText = ttk.StringVar(self)
        self._findFrame = ttk.Frame(self._text)

        self._findEntry = tkEntryWithPlaceholder(
            self._findFrame,
            placeholder='Find..',
            autostyle=False,
            font=findFont,
            borderwidth=0,
            insertwidth=2,
            highlightthickness=0,
            background=findBackground,
            foreground=textFontColor,
            insertbackground=cursorColor,
            textvariable=self._findText)
        self._findEntry.pack(side=LEFT, pady=2, padx=(10, 4))

        #Import the image using PhotoImage function
        self._findButtonImg= ttk.PhotoImage(file='assets/x1.png')

        self._findCloseButton = tk.Button(
            self._findFrame,
            autostyle=False,
            image=self._findButtonImg,
            borderwidth=0,
            highlightthickness=0,
            background=darkBackgroundColor,
            activebackground=lighterDarkBackgroundColor,
            relief=FLAT,
            command=self._closeSearch)
        self._findCloseButton.pack(side=LEFT, expand=NO, pady=2, padx=(0, 4))

        self._text.bind_all('<Control-KeyPress-f>', lambda e: self._openSearch(), add='+')
        self._text.bind_all('<Escape>', lambda e: self._closeSearch(), add='+')

        self.log('<<LOGGER INITIALIZED>>',INFO)

    def log(self, message:str, logLevel):
        """Add a message to the logger. Each message has a logLevel assosiated
        with it.

        LOG LEVEL OPTIONS

        DEBUG, INFO, WARNING, ERROR, SUCCESS
        """

        timestamp = ''
        if self._timestamp:
            timestamp = time.strftime(f'%H:%M:%S::', time.localtime())

        tag = f'tag_{logLevel}'
        self._text.configure(state=NORMAL)
        self._text.insert(END, timestamp, 'timestamp_tag')
        self._text.insert(END, f'{message}\n', tag)
        self._text.configure(state=DISABLED)

    def _onChange(self, _):
        pass

    def _openSearch(self):
        self._findFrame.place(relx=0.98, rely=0, anchor=NE, bordermode=OUTSIDE)
        self._isSearchOpen = True

    def _closeSearch(self):
        self._findFrame.place_forget()
        self._isSearchOpen = False



if __name__ == "__main__":

    window = ttk.Window("Certificates Creation", themename="darkly")
    window.geometry('1600x800')

    window.rowconfigure(0, weight=1)  # make the CanvasImage widget expandable
    window.columnconfigure(0, weight=1)
    imageViwer = CanvasImage(window, 'assets/nice.jpg')
    imageViwer.pack(fill=BOTH, expand=YES)

    window.mainloop()