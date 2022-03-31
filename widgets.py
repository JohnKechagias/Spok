import math
import tkinter as tk
import warnings

from PIL import Image, ImageTk, ImageSequence
from itertools import cycle
from functools import partial

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from helperFuncs import containToRange



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
    def __init__(self, master, imagePath, *args, **kw_args):
        super().__init__(master)

        self.topFrame = ttk.Frame(self)
        self.topFrame.pack(side=TOP, fill=X, pady=5)

        self.imageCanvas = CanvasImage(self, imagePath)
        self.imageCanvas.pack(expand=YES, fill=BOTH, side=BOTTOM)

        self.xCoordLabel = ttk.Label(self.topFrame, text='X: ')
        self.xCoordLabel.pack(side=LEFT, padx=(0, 3))

        self.xCoordEntry = ttk.Entry(self.topFrame, textvariable=self.imageCanvas.xCoord, width=4, bootstyle=DARK)
        self.xCoordEntry.pack(side=LEFT, padx=(0, 15))

        self.yCoordLabel = ttk.Label(self.topFrame, text='Y: ')
        self.yCoordLabel.pack(side=LEFT, padx=(0, 3))

        self.yCoordEntry = ttk.Entry(self.topFrame, textvariable=self.imageCanvas.yCoord, width=4, bootstyle=DARK)
        self.yCoordEntry.pack(side=LEFT)


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
    def __init__(self, master, path, x=None, y=None):
        super().__init__(master)
        """ Initialize the ImageFrame """
        self.imScale = 1.0  # scale for the canvas image zoom, public for outer classes
        self._delta = 1.3  # zoom magnitude
        self._filter = Image.NEAREST  # could be: NEAREST, BILINEAR, BICUBIC and ANTIALIAS
        self._previous_state = 0  # previous state of the keyboard
        self.path = path  # path to the image, should be public for outer classes

        # Create ImageFrame in placeholder widget
        # Vertical and horizontal scrollbars for canvas
        self.rowconfigure(0, weight=1)  # make the CanvasImage widget expandable
        self.columnconfigure(0, weight=1)
        hbar = AutoScrollbar(self, orient=HORIZONTAL)
        vbar = AutoScrollbar(self, orient=VERTICAL)
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
        self.__huge = False  # huge or not
        self.__huge_size = 14000  # define size of the huge image
        self.__band_width = 1024  # width of the tile band
        Image.MAX_IMAGE_PIXELS = 1000000000  # suppress DecompressionBombError for the big image
        
        with warnings.catch_warnings():  # suppress DecompressionBombWarning
            warnings.simplefilter('ignore')
            self.__image = Image.open(self.path)  # open image, but down't load it
        self.imwidth, self.imheight = self.__image.size  # public for outer classes

        self._currCenter = [0, 0]  # coordinate center
        self._imageCoversXaxis = FALSE
        self._imageCoversYaxis = FALSE

        self.xCoord = tk.IntVar(value=0)
        self.yCoord = tk.IntVar(value=0)

        if self.imwidth * self.imheight > self.__huge_size * self.__huge_size and \
           self.__image.tile[0][0] == 'raw':  # only raw images could be tiled
            self.__huge = True  # image is huge
            self.__offset = self.__image.tile[0][2]  # initial tile offset
            self.__tile = [self.__image.tile[0][0],  # it have to be 'raw'
                           [0, 0, self.imwidth, 0],  # tile extent (a rectangle)
                           self.__offset,
                           self.__image.tile[0][3]]  # list of arguments to the decoder
        self._minSide = min(self.imwidth, self.imheight)  # get the smaller image side
        # Create image pyramid
        self._pyramid = [self.smaller()] if self.__huge else [Image.open(self.path)]
        # Set ratio coefficient for image pyramid
        self._ratio = max(self.imwidth, self.imheight) / self.__huge_size if self.__huge else 1.0
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
        self._showImage()  # show image on the canvas
        self.canvas.focus_set()  # set focus on the canvas

    def smaller(self):
        """ Resize image proportionally and return smaller image """
        w1, h1 = float(self.imwidth), float(self.imheight)
        w2, h2 = float(self.__huge_size), float(self.__huge_size)
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
        i, j, n = 0, 1, round(0.5 + self.imheight / self.__band_width)
        while i < self.imheight:
            print('\rOpening image: {j} from {n}'.format(j=j, n=n), end='')
            band = min(self.__band_width, self.imheight - i)  # width of the tile band
            self.__tile[1][3] = band  # set band width
            self.__tile[2] = self.__offset + self.imwidth * i * 3  # tile offset (3 bytes per pixel)
            self.__image.close()
            self.__image = Image.open(self.path)  # reopen / reset image
            self.__image.size = (self.imwidth, band)  # set size of the tile band
            self.__image.tile = [self.__tile]  # set tile
            cropped = self.__image.crop((0, 0, self.imwidth, band))  # crop tile band
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
            if self.__huge and self._currImg < 0:  # show huge image
                h = int((y2 - y1) / self.imScale)  # height of the tile band
                self.__tile[1][3] = h  # set the tile band height
                self.__tile[2] = self.__offset + self.imwidth * int(y1 / self.imScale) * 3
                self.__image.close()
                self.__image = Image.open(self.path)  # reopen / reset image
                self.__image.size = (self.imwidth, h)  # set size of the tile band
                self.__image.tile = [self.__tile]
                image = self.__image.crop((int(x1 / self.imScale), 0, int(x2 / self.imScale), h))
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
            if newImScale < 1: return  # don't allow the image to become smaller than its normal size
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
        if self.__huge:  # image is huge and not totally in RAM
            band = bbox[3] - bbox[1]  # width of the tile band
            self.__tile[1][3] = band  # set the tile height
            self.__tile[2] = self.__offset + self.imwidth * bbox[1] * 3  # set offset of the band
            self.__image.close()
            self.__image = Image.open(self.path)  # reopen / reset image
            self.__image.size = (self.imwidth, band)  # set size of the tile band
            self.__image.tile = [self.__tile]
            return self.__image.crop((bbox[0], 0, bbox[2], band))
        else:  # image is totally in RAM
            return self._pyramid[0].crop(bbox)

    def destroy(self):
        """ ImageFrame destructor """
        self.__image.close()
        map(lambda i: i.close, self._pyramid)  # close all pyramid images
        del self._pyramid[:]  # delete pyramid list
        del self._pyramid  # delete pyramid variable
        self.canvas.destroy()
        self.destroy()


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
        return self.fromRGB(colorRGBTuple)

    @staticmethod
    def fromRGB(rgb):
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


if __name__ == "__main__":

    app = ttk.Window("Certificates Creation", themename="darkly")
    app.geometry('1600x800')

    app.rowconfigure(0, weight=1)  # make the CanvasImage widget expandable
    app.columnconfigure(0, weight=1)
    imageViwer = CanvasImage(app, 'assets/nice.jpg')
    imageViwer.pack(fill=BOTH, expand=YES)

    app.mainloop()