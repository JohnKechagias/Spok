import math
from pathlib import Path
from typing import Literal, Optional
import warnings
from PIL import Image, ImageTk

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk

from widgets.image_button import ImageButton

from .auto_scrollbar import AutoScrollbar



class ImageViewer(ttk.Frame):
    def __init__(
        self,
        master: tk.Widget = None,
        imagepath: Path = None,
        text_alignment: Literal['left', 'middle', 'right'] = LEFT,
        xcoord: int = 0,
        ycoord: int = 0,
        tree_height: int = 1,
        tree_max_height: int = 9,
        *args,
        **kwArgs
    ) -> None:
        super().__init__(master)

        self.background_color = '#222222'
        # The number of saved coords. The curr_coord is
        # also included. So, _tree_size = num of entries + 1.
        # Should only be accessed by the property tree_size.
        self._tree_size = 1
        self.tree_max_height = tree_max_height

        # =-=-=-=-=-=-=-=-=- Top frame -=-=-=-=-=-=-=-=-=-=-=

        self.top_frame = ttk.Frame(self)
        self.top_frame.pack(side=TOP, fill=X, pady=5)

        self.image_canvas = CanvasImage(
            self,
            bootstyle=(DEFAULT, ROUND),
            path=imagepath,
            *args,
            **kwArgs
        )
        self.image_canvas.pack(side=TOP, expand=YES, fill=BOTH)

        # =-=-=-=-=-=-=-=- Canvas Coords -=-=-=-=-=-=-=-=-=-=

        self.x_coord_label = ttk.Label(self.top_frame, text='X: ')
        self.x_coord_label.pack(side=LEFT, padx=(0, 3))

        self.x_coord_entry = ttk.Entry(
            self.top_frame,
            textvariable=self.image_canvas.temp_x_coord,
            width=4,
            bootstyle=DARK
        )
        self.x_coord_entry.pack(side=LEFT, padx=(0, 15))

        self.y_coord_label = ttk.Label(self.top_frame, text='Y: ')
        self.y_coord_label.pack(side=LEFT, padx=(0, 3))

        self.y_coord_entry = ttk.Entry(
            self.top_frame,
            textvariable=self.image_canvas.temp_y_coord,
            width=4,
            bootstyle=DARK
        )
        self.y_coord_entry.pack(side=LEFT, padx=(0, 40))

        # =-=-=-=-=-=-=-=- Text Alignment -=-=-=-=-=-=-=-=-=-=

        self.text_alignment = ttk.StringVar()
        self.text_alignment_list = ('left', 'middle', 'right')
        self.text_alignment_combobox = ttk.Combobox(
            master=self.top_frame,
            bootstyle=(SECONDARY),
            state=READONLY,
            textvariable=self.text_alignment,
            width=6,
            values=self.text_alignment_list
        )
        item_index = self.text_alignment_list.index(text_alignment)
        self.text_alignment_combobox.current(item_index)
        self.text_alignment_combobox.pack(side=LEFT)

        # =-=-=-=-=-=-=-=-=- TreeView -=-=-=-=-=-=-=-=-=-=-=

        self.tree_frame = ttk.Frame(
            self,
            bootstyle=SECONDARY,
            borderwidth=4
        )

        self.tree_frame.bind('<ButtonPress-3>',
            self._hide_tree, add='+')

        # Make tree resizable
        self.rowconfigure(0, weight=1)

        # Define columns
        self._columns = ('index', 'x', 'y')
        self._tree_is_visible = False
        # Is used to hold the old curr cord
        # so we can add it to the tree
        self._old_curr_coord = None

        self._tree = ttk.Treeview(
            self.tree_frame,
            bootstyle=DARK,
            columns=self._columns,
            selectmode=BROWSE,
            height=self.tree_size - 1,
            show=HEADINGS
        )
        self._tree.grid(row=0, column=0, sticky=NSEW)

        # Setup scrollbar
        self._scrollbar = AutoScrollbar(
            self.tree_frame,
            orient=VERTICAL,
            bootstyle=DEFAULT,
            command=self._tree.yview
        )

        self._tree.configure(yscroll=self._scrollbar.set)
        self._scrollbar.grid(row=0, column=1, sticky=NS)

        self._tree.column('#1', stretch=NO, width=46)
        self._tree.column('#2', width=38, anchor=CENTER)
        self._tree.column('#3', width=38, anchor=CENTER)

        self._tree.heading('index', text='Index')
        self._tree.heading('x', text='X')
        self._tree.heading('y', text='Y')

        self.image_canvas.saved_x_coord.set(xcoord)
        self.image_canvas.saved_y_coord.set(ycoord)

        self._tree.bind(
            '<Double-ButtonPress-1>',
            self._on_entry_double_clicked,
            add='+'
        )

        self._tree.bind('<ButtonPress-3>',
            self._hide_tree, add='+')

        #TODO Load saved coords

        # =-=-=-=-=-=-=-=- Saved Coords -=-=-=-=-=-=-=-=-=-=

        self.curr_coord_frame = ttk.Frame(
            self.top_frame,
            bootstyle=SECONDARY,
            borderwidth=2
        )
        self.curr_coord_frame.pack(side=RIGHT)

        self.curr_coord_frame.bind('<Double-ButtonPress-1>',
            self._show_tree, add='+')

        self.curr_coord_frame.bind('<ButtonPress-3>',
            self._hide_tree, add='+')

        self.buttons_frame = ttk.Frame(self.top_frame)
        self.buttons_frame.pack(side=RIGHT, padx=(0, 8))

        self.add_coord_button = ImageButton(
            self.buttons_frame,
            codename='add',
            background=self.background_color,
            command=self._add_saved_coord_entry
        )
        self.add_coord_button.pack(side=TOP)

        self.remove_coord_button = ImageButton(
            self.buttons_frame,
            codename='minus',
            background=self.background_color,
            command=self._remove_saved_coord_entry
        )
        self.remove_coord_button.pack(side=BOTTOM)

        # Holds the curr_coords index
        self.index = tk.StringVar(value='1')

        self.index_coord_entry = ttk.Entry(
            self.curr_coord_frame,
            textvariable=self.index,
            width=4,
            bootstyle=SECONDARY,
            state=READONLY
        )
        self.index_coord_entry.pack(side=LEFT, padx=(0, 2))

        self.index_coord_entry.bind('<Double-ButtonPress-1>',
            self._show_tree, add='+')

        self.index_coord_entry.bind('<ButtonPress-3>',
            self._hide_tree, add='+')

        self.x_curr_coord_entry = ttk.Entry(
            self.curr_coord_frame,
            textvariable=self.image_canvas.saved_x_coord,
            width=4,
            bootstyle=SECONDARY,
            state=READONLY
        )
        self.x_curr_coord_entry.pack(side=LEFT, padx=(0, 2))

        self.x_curr_coord_entry.bind('<Double-ButtonPress-1>',
            self._show_tree, add='+')

        self.x_curr_coord_entry.bind('<ButtonPress-3>',
            self._hide_tree, add='+')

        self.y_curr_coord_entry = ttk.Entry(
            self.curr_coord_frame,
            textvariable=self.image_canvas.saved_y_coord,
            width=4,
            bootstyle=SECONDARY,
            state=READONLY
        )
        self.y_curr_coord_entry.pack(side=LEFT)

        self.y_curr_coord_entry.bind('<Double-ButtonPress-1>',
            self._show_tree, add='+')

        self.y_curr_coord_entry.bind('<ButtonPress-3>',
            self._hide_tree, add='+')

    @property
    def tree_size(self) -> int:
        return self._tree_size

    @tree_size.setter
    def tree_size(self, value: int):
        self._tree_size = value
        # Update tree height. Height can't be larger than
        # tree_max_height.
        tree_height = min(self._tree_size - 1, self.tree_max_height)
        self._tree.configure(height=tree_height)

    def _show_tree(self, event: tk.Event):
        if self._tree_is_visible:
            return

        self.tree_frame.place(
            relx=1,
            y=38,
            width=134,
            anchor=NE,
            bordermode=OUTSIDE
        )
        self._tree_is_visible = True

    def _hide_tree(self, event: tk.Event):
        if not self._tree_is_visible:
            return

        self.tree_frame.place_forget()
        self._tree_is_visible = False

    def _on_entry_double_clicked(self, event: tk.Event):
        """ Callback for when a TreeView entry is double clicked. """
        # We must first save the curr coord to a temp var,
        # then set the new curr coord and lastly add the
        # old curr coord to the tree. We can't just add the
        # curr coord to the tree and then set the new coord,
        # because that causes a bug where if the user presses
        # the consecutively very quickly the new tree entry
        # (which is the old curr coord) gets duplicated.
        self._swap_curr_coord()

    def _swap_curr_coord(self, index: Optional[int] = None):
        """ Swap the current coord with a coord in the tree
        and save the old current coord in the tree.

        Args:
            index: The index of the tree coord to swap the
                current coord with. If the index is None,
                the top coord from the tree selection is
                set as the current coord instead.
        """
        values = [
            self.index.get(),
            self.image_canvas.saved_x_coord.get(),
            self.image_canvas.saved_y_coord.get()
        ]
        # Save curr coord to a temp var
        self._old_curr_coord = values

        try:
            if index is not None:
                entry_to_set = self._tree.get_children()[index]
            else:
                entry_to_set = self._tree.selection()[0]
        except IndexError:
            return
        values = self._tree.item(entry_to_set)['values']
        self.index.set(values[0])
        self.image_canvas.saved_x_coord.set(values[1])
        self.image_canvas.saved_y_coord.set(values[2])

        # Add old curr coord to the tree
        tree_index = int(self._old_curr_coord[0]) - 1
        self._tree.insert('', tree_index, values=self._old_curr_coord)

        # Delete new curr coord from the tree
        self._tree.delete(entry_to_set)

    def _add_saved_coord_entry(self, *args):
        """ Add a new saved coord entry to the tree. """
        self.tree_size += 1
        values =  [self.tree_size, 0, 0]
        self._tree.insert('', END, values=values)

    def _remove_saved_coord_entry(self, *_):
        """ Remove the saved coord entry with the largest index
        from the tree. The current coord is also included. If the
        current coord is the entry with the largest index, its
        place is given to the coord with the new largest index
        (former 2nd largest index). """
        # If only one coord exists (the current coord),
        # don't delete it
        if self.tree_size == 1:
            return

        # If the current coord is the last in the tree
        # (largest index), remove it and give its place
        # to the coord with the new largest index
        # (former 2nd largest index)
        if int(self.index.get()) == self.tree_size:
            self._swap_curr_coord(-1)

        try:
            entry_to_delete = self._tree.get_children()[-1]
        except IndexError:
            return
        self._tree.delete(entry_to_delete)
        self.tree_size -= 1

    def get_saved_coords(self) -> tuple[int, int]:
        """ Return saved coords. """
        return (self.image_canvas.saved_x_coord.get(),
                self.image_canvas.saved_y_coord.get())

    def load_image(self, path:str):
        """ Delete current image and load a new image into the canvas. """
        self.image_canvas.load_image(path)


class CanvasImage(ttk.Frame):
    """ Display and zoom image. """
    def __init__(
        self,
        master=None,
        bootstyle=DEFAULT,
        path=None,
        disable_zoom_out=False
    ) -> None:
        super().__init__(master)
        """ Initialize the ImageFrame. """
        self.im_scale = 1.0  # Scale for the canvas image zoom, public for outer classes
        self._delta = 1.3  # Zoom magnitude
        self._filter = Image.NEAREST  # Could be: NEAREST, BILINEAR, BICUBIC and ANTIALIAS
        self._image = None
        self.disable_zoom_out = disable_zoom_out # Allows the image to become smaller than its original size

        # Create ImageFrame in placeholder widget
        # Vertical and horizontal scrollbars for canvas
        self.rowconfigure(0, weight=1)  # make the CanvasImage widget expandable
        self.columnconfigure(0, weight=1)
        _hbar = AutoScrollbar(self, bootstyle=bootstyle, orient=HORIZONTAL)
        _vbar = AutoScrollbar(self, bootstyle=bootstyle, orient=VERTICAL)
        _hbar.grid(row=1, column=0, sticky=EW)
        _vbar.grid(row=0, column=1, sticky=NS)

        # Create canvas and bind it with scrollbars. Public for outer classes
        self._canvas = ttk.Canvas(
            self,
            highlightthickness=0,
            xscrollcommand=_hbar.set,
            yscrollcommand=_vbar.set
        )
        self._canvas.grid(row=0, column=0, sticky=NSEW)
        self._canvas.update()  # Wait till canvas is created
        _hbar.configure(command=self._scroll_X)  # Bind scrollbars to the canvas
        _vbar.configure(command=self._scroll_Y)

        # Bind events to the Canvas
        self._canvas.bind('<Configure>', lambda _: self._show_image())  # Canvas is resized
        self._canvas.bind('<ButtonPress-1>', self._move_from)  # Remember canvas position
        self._canvas.bind('<B1-Motion>',     self._move_to)  # Move canvas to the new position
        self._canvas.bind('<MouseWheel>', self._wheel)  # Zoom for Windows and MacOS, but not Linux
        self._canvas.bind('<Button-5>',   self._wheel)  # Zoom for Linux, wheel scroll down
        self._canvas.bind('<Button-4>',   self._wheel)  # Zoom for Linux, wheel scroll up
        self._canvas.bind('<Motion>',     self._on_mouse_movement)
        self._canvas.bind('<Button-3>',   self._save_coordinates)
        # Handle keystrokes in idle mode, because program slows down on a weak computers,
        # when too many key stroke events in the same time
        self._canvas.bind('<Key>',
            lambda event: self._canvas.after_idle(self._on_keystroke, event)
        )

        # Decide if this image huge or not
        self._huge = False  # Huge or not
        self._huge_size = 14000  # Define size of the huge image
        self._band_width = 1024  # Width of the tile band

        # Current pixel coords (the image pixel in which the mouse is inside)
        self.temp_x_coord = ttk.IntVar(value=0)
        self.temp_y_coord = ttk.IntVar(value=0)

        # Saved pixel coords
        self.saved_x_coord = ttk.IntVar(value=0)
        self.saved_y_coord = ttk.IntVar(value=0)

        # Load image in canvas
        if path is not None:
            self.load_image(path)
        else:
            self._container = self._canvas.create_rectangle(
                (0, 0, 0, 0), width=0)

    def get_saved_coordinates(self):
        """ Return the save coords. """
        return (self.saved_x_coord.get(), self.saved_y_coord.get())

    def load_image(self, path: str):
        """ Delete current image and load a new image into the canvas. """
        if self._image is not None:
            self._image.close()
            self._canvas.delete(self._container)
            map(lambda i: i.close(), self._pyramid)  # Close all pyramid images

        self.im_scale = 1.0
        self._previous_state = 0  # Previous state of the keyboard
        self.path = path  # Path to the image, should be public for outer classes

        self._top_left_corner = [0, 0]  # Coordinate center
        self._image_wider_than_canvas = False
        self._image_taller_than_canvas = True

        with warnings.catch_warnings():  # Suppress DecompressionBombWarning
            warnings.simplefilter('ignore')
            self._image = Image.open(self.path)  # Open image, but down't load it
        self.im_width, self.im_height = self._image.size  # Public for outer classes
        self._min_side = min(self.im_width, self.im_height)  # Get the smaller image side
        # Create image pyramid
        self._pyramid = [Image.open(self.path)]
        # Set ratio coefficient for image pyramid
        self._ratio = 1.0
        self._curr_img = 0  # Current image from the pyramid
        self._scale = self.im_scale * self._ratio  # Image pyramide scale
        self._reduction = 2  # Reduction degree of image pyramid
        w, h = self._pyramid[-1].size
        while w > 512 and h > 512:  # Top pyramid image is around 512 pixels in size
            w /= self._reduction  # Divide on reduction degree
            h /= self._reduction  # Divide on reduction degree
            self._pyramid.append(self._pyramid[-1].resize((int(w), int(h)), self._filter))
        # Put image into container rectangle and use it to set proper coordinates to the image
        self._container = self._canvas.create_rectangle((0, 0, self.im_width, self.im_height), width=0)

        self._canvas.scan_dragto(0, 0, gain=1)
        self._show_image()  # Zoom tile and show it on the canvas
        self._canvas.focus_set()  # Set focus on the canvas

    def _scroll_X(self, *args, **kwargs):
        """ Scroll canvas horizontally and redraw the image. """
        self._canvas.xview(*args)  # Scroll horizontally
        self._show_image()  # Redraw the image

    def _scroll_Y(self, *args, **kwargs):
        """ Scroll canvas vertically and redraw the image. """
        self._canvas.yview(*args)  # Scroll vertically
        self._show_image()  # Redraw the image

    def _show_image(self):
        """ Show image on the Canvas. Implements correct image zoom
        almost like in Google Maps. """
        box_image = self._canvas.coords(self._container)  # Get image area
        box_canvas = (
            self._canvas.canvasx(0),  # Get visible area of the canvas
            self._canvas.canvasy(0),
            self._canvas.canvasx(self._canvas.winfo_width()),
            self._canvas.canvasy(self._canvas.winfo_height())
        )

        box_img_int = tuple(map(int, box_image))  # Convert to integer or it will not work properly
        # Get scroll region box
        box_scroll = [
            min(box_img_int[0], box_canvas[0]),
            min(box_img_int[1], box_canvas[1]),
            max(box_img_int[2], box_canvas[2]),
            max(box_img_int[3], box_canvas[3])
        ]

        # Horizontal part of the image is in the visible area
        if  box_scroll[0] == box_canvas[0] and box_scroll[2] == box_canvas[2]:
            box_scroll[0]  = box_img_int[0]
            box_scroll[2]  = box_img_int[2]
        # Vertical part of the image is in the visible area
        if  box_scroll[1] == box_canvas[1] and box_scroll[3] == box_canvas[3]:
            box_scroll[1]  = box_img_int[1]
            box_scroll[3]  = box_img_int[3]

        # Set current center value
        curr_image_width = self.im_width * self.im_scale
        curr_image_height = self.im_height * self.im_scale

        # Check if image fills the x-axis of the canvas
        # If image is wider than the canvas move it
        # so it occupies the whole x axis
        if self._canvas.winfo_width() > curr_image_width:
            self._image_wider_than_canvas = False
            self._top_left_corner[0] = self._canvas.canvasx(0) - box_scroll[0]
        else:
            self._image_wider_than_canvas = True
            # Image distance from canvas left side
            distance_from_left_side = math.ceil(box_scroll[0] - box_image[0])
            # Image distance from canvas right side
            distance_from_right_side = math.ceil(box_scroll[2] - box_image[2])

            if distance_from_left_side < 0:
                self._canvas.move(self._container, distance_from_left_side, 0)
                box_scroll[2] += distance_from_left_side
            elif distance_from_right_side > 0:
                self._canvas.move(self._container, distance_from_right_side, 0)
                box_scroll[0] += distance_from_right_side

        # Check if image fills the y-axis of the canvas
        # If image is taller than the canvas move it
        # so it occupies the whole Y axis
        if self._canvas.winfo_height() > curr_image_height:
            self._image_taller_than_canvas = False
            self._top_left_corner[1] = self._canvas.canvasy(0) - box_scroll[1]
        else:
            self._image_taller_than_canvas = True
            # Image distance from canvas top side
            distance_from_top_side = math.ceil(box_scroll[1] - box_image[1])
            # Image distance from canvas right side
            distance_from_bottom_side = math.ceil(box_scroll[3] - box_image[3])

            if distance_from_top_side < 0:
                self._canvas.move(self._container, 0, distance_from_top_side)
                box_scroll[3] += distance_from_top_side
            elif distance_from_bottom_side > 0:
                self._canvas.move(self._container, 0, distance_from_bottom_side)
                box_scroll[1] += distance_from_bottom_side

        # Recalculate containers coords
        box_image = self._canvas.coords(self._container)
        box_img_int = tuple(map(int, box_image))

        self._canvas.configure(scrollregion=tuple(map(int, box_scroll)))  # Set scroll region

        x1 = max(box_canvas[0] - box_image[0], 0)  # Get coordinates (x1,y1,x2,y2) of the image tile
        y1 = max(box_canvas[1] - box_image[1], 0)
        x2 = min(box_canvas[2], box_image[2]) - box_image[0]
        y2 = min(box_canvas[3], box_image[3]) - box_image[1]

        # Calculate current image center
        if self._image_wider_than_canvas:
            self._top_left_corner[0] = round(x1 / self.im_scale)
        if self._image_taller_than_canvas:
            self._top_left_corner[1] = round(y1 / self.im_scale)

        if int(x2 - x1) > 0 and int(y2 - y1) > 0:  # Show image if it in the visible area
            image = self._pyramid[max(0, self._curr_img)].crop(  # Crop current img from pyramid
                (int(x1 / self._scale), int(y1 / self._scale),
                int(x2 / self._scale), int(y2 / self._scale))
            )
            image_tk = ImageTk.PhotoImage(image.resize((int(x2 - x1), int(y2 - y1)), self._filter))
            image_id = self._canvas.create_image(
                max(box_canvas[0], box_img_int[0]),
                max(box_canvas[1], box_img_int[1]),
                anchor=NW,
                image=image_tk
            )
            self._canvas.lower(image_id)  # Set image into background
            self._canvas.imagetk = image_tk  # Keep an extra reference to prevent garbage-collection

    def _move_from(self, event: tk.Event):
        """ Remember previous coordinates for scrolling with the mouse. """
        self.last_pos = (event.x, event.y)
        self._canvas.scan_mark(event.x, event.y)

    def _move_to(self, event: tk.Event):
        """ Drag (move) canvas to the new position. """
        self._canvas.scan_dragto(event.x, event.y, gain=1)
        self._show_image()  # Zoom tile and show it on the canvas

    def _outside(self, x: int, y: int):
        """ Checks if the point `(x,y)` is outside the image area. """
        bbox = self._canvas.coords(self._container)  # Get image area
        if bbox[0] < x < bbox[2] and bbox[1] < y < bbox[3]:
            return False  # Point (x,y) is inside the image area
        else:
            return True  # Point (x,y) is outside the image area

    def _wheel(self, event: tk.Event):
        """ Zoom with mouse wheel. """
        x = self._canvas.canvasx(event.x)  # Get coordinates of the event on the canvas
        y = self._canvas.canvasy(event.y)
        if self._outside(x, y): return  # Zoom only inside image area
        scale = 1.0
        # Respond to Linux (event.num) or Windows (event.delta) wheel event
        if event.num == 5 or event.delta == -120:  # Scroll down, smaller
            if round(self._min_side * self.im_scale) < 30: return  # Image is less than 30 pixels
            self.im_scale /= self._delta
            scale         /= self._delta
            # Use BICUBIC filtering to make the zoomed out image smoother
            if self.im_scale < 1.0: self._filter = Image.BICUBIC
        if event.num == 4 or event.delta == 120:  # Scroll up, bigger
            i = min(self._canvas.winfo_width(), self._canvas.winfo_height()) >> 1
            if i < self.im_scale: return  # 1 pixel is bigger than the visible area
            self.im_scale *= self._delta
            scale         *= self._delta
            # Use NEAREST filtering to make the pixels visisble
            if self.im_scale > 1.0:
                self._filter = Image.NEAREST
        # Take appropriate image from the pyramid
        k = self.im_scale * self._ratio  # Temporary coefficient
        self._curr_img = min((-1) * int(math.log(k, self._reduction)), len(self._pyramid) - 1)
        self._scale = k * math.pow(self._reduction, max(0, self._curr_img))
        self._canvas.scale(ALL, x, y, scale, scale)  # Escale all objects
        self._show_image()

    def _on_keystroke(self, event: tk.Event):
        """ Scrolling with the keyboard. Independent from the language of
        the keyboard, CapsLock, <Ctrl>+<key>, etc. """
        if event.state - self._previous_state == 4:  # Means that the Control key is pressed
            return  # Do nothing if Control key is pressed
        self._previous_state = event.state  # Remember the last keystroke state
        # Up, Down, Left, Right keystrokes
        if event.keycode in [40, 114, 85]:  # Scroll right: keys 'D', 'Right' or 'Numpad-6'
            self._scroll_X('scroll',  1, 'unit', event=event)
        elif event.keycode in [38, 113, 83]:  # Scroll left: keys 'A', 'Left' or 'Numpad-4'
            self._scroll_X('scroll', -1, 'unit', event=event)
        elif event.keycode in [25, 111, 80]:  # Scroll up: keys 'W', 'Up' or 'Numpad-8'
            self._scroll_Y('scroll', -1, 'unit', event=event)
        elif event.keycode in [39, 116, 88]:  # Scroll down: keys 'S', 'Down' or 'Numpad-2'
            self._scroll_Y('scroll',  1, 'unit', event=event)

    def _save_coordinates(self, event: tk.Event):
        """ Save current `temp_coords` to `saved_coords`. """
        self.saved_x_coord.set(self.temp_x_coord.get())
        self.saved_y_coord.set(self.temp_y_coord.get())

    def _canvas_coords_to_image_coords(self, x: int, y: int):
        """ Convert canvas coords to image coords.
        The center of the image is its top left corner. """
        if self._image_wider_than_canvas:
            x_coord = int(self._top_left_corner[0] + (x / self.im_scale))
        else:
            x_coord = int((self._top_left_corner[0] + x) / self.im_scale)

        if self._image_taller_than_canvas:
            y_coord = int(self._top_left_corner[1] + (y / self.im_scale))
        else:
            y_coord = int((self._top_left_corner[1] + y) / self.im_scale)

        # Because the coords conversion isn't totally accurate,
        # we make sure that the coords returned are inside the image.
        x_coord = min(x_coord, self.im_width - 1)
        y_coord = min(y_coord, self.im_height - 1)
        return (x_coord, y_coord)

    def _on_mouse_movement(self, event: tk.Event):
        """ Convert the current mouse coords to image coords
        and store them to `temp_coords`. """
        x = self._canvas.canvasx(event.x)
        y = self._canvas.canvasy(event.y)
        if self._outside(x, y): return
        temp = self._canvas_coords_to_image_coords(event.x, event.y)
        self.temp_x_coord.set(temp[0])
        self.temp_y_coord.set(temp[1])
