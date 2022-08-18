from typing import Union
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

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

        self.font = ('Arial', '14')

        self.container_frame = ttk.Frame(self, bootstyle=INFO)
        self.container_frame.grid(row=0, column=0)

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
        self.font_frame.columnconfigure(5, weight=1)
        self.font_frame.columnconfigure(6, weight=1)


        self._columns = ('font', 'size', 'color', 'weight',
            'slant', 'effects', 'preview')

        self.columns = []

        for index, col in enumerate(self._columns):
            col_label = ttk.Label(
                self.font_frame,
                bootstyle=(INVERSE, DARK),
                text=col,
                justify=LEFT,
                font=self.font
            )
            col_label.grid(row=0, column=index, sticky=NSEW, padx=1, pady=1)
            self.columns.append(col_label)

    def add_font_settings(self): ...

    def remove_font_settings(self, row_index: Union[int, END]):
        if row_index == END:
            row_index = -1
