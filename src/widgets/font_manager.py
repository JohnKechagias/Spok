from typing import Literal, Union
import tkinter as tk
from tkinter.font import *
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from widgets.constants import Hex

from widgets.scrollable_frame import ScrollableFrame



class FontManager(ttk.Frame):
    def __init__(
        self,
        master=None,
        bootstyle=DEFAULT,
        scrollbar_bootstyle=DEFAULT,
        *args,
        **kwargs,
    ) -> None:
        """ Construct a Ttk Treeview with parent master.

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
        super().__init__(master, padding=10)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.container_frame = ttk.Frame(self, bootstyle=INFO)
        self.container_frame.grid(row=0, column=0, sticky=NSEW)

        self._font_frame_container = ScrollableFrame(
            self.container_frame,
            bootstyle=SECONDARY,
            frame_bootstyle=SECONDARY,
            scrollbar_bootstyle=scrollbar_bootstyle,
            padding=10
        )
        self._font_frame_container.pack(expand=YES, fill=BOTH, anchor=NW)

        self.font_frame = self._font_frame_container.frame
        self.font_frame.columnconfigure(0, weight=1)
        self.font_frame.columnconfigure(1, weight=1)
        self.font_frame.columnconfigure(6, weight=1)
        self.font_frame.columnconfigure(7, weight=1)

        self._columns = ('name', 'font', 'size', 'color', 'weight',
            'slant', 'effects', 'preview')
        self._num_of_cols = len(self._columns)
        self.columns = []
        self.last_row = 0

        self.add_font_settings(*self._columns)

    def add_font_settings(
        self,
        name: str,
        family: str,
        size: int,
        color: Hex,
        weight: Literal['normal', 'bold'] = NORMAL,
        slant: Literal['roman', 'italic'] = ROMAN,
        underline: bool = True,
        overstrike: bool = True
    ):
        font_info = (name, family, str(size), color, weight, slant, str(underline), str(overstrike))
        col_labels = []

        for index in range(self._num_of_cols):
            col_label = ttk.Label(
                self.font_frame,
                bootstyle=(INVERSE, DARK),
                text=font_info[index],
                justify=LEFT
            )
            col_label.grid(row=self.last_row, column=index, sticky=NSEW, padx=1, pady=1)
            col_labels.append(col_label)
        self.columns.append(col_labels)
        self.last_row += 1

    def remove_font_settings(self, row_index: Union[int, END]):
        if row_index == END:
            row_index = -1
        
        for label in self.columns[row_index]:
            label.grid_remove()
        self.columns.pop(row_index)
