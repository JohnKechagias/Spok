import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from widgets.auto_scrollbar import AutoScrollbar



class ScrollableFrame(ttk.Frame):
    def __init__(
        self,
        master: tk.Widget,
        bootstyle: str = DEFAULT,
        frame_bootstyle: str = SECONDARY,
        scrollbar_bootstyle: str = DEFAULT,
        *args,
        **kwargs
    ):
        super().__init__(master, bootstyle=bootstyle, *args, **kwargs)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.canvas = ttk.Canvas(self)
        self.canvas.grid(row=0, column=0, sticky=NSEW)

        self.scrollbar = AutoScrollbar(
            self,
            bootstyle=scrollbar_bootstyle,
            orient=VERTICAL,
            command=self.canvas.yview
        )
        self.scrollbar.grid(row=0, column=1, sticky=NS)

        self.frame = ttk.Frame(self.canvas, bootstyle=frame_bootstyle)
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)

        self.frame.bind(
            '<Configure>',
            lambda _: self.canvas.configure(
                scrollregion=self.canvas.bbox(ALL)
            )
        )

        self.canvas.create_window(
            (0, 0),
            window=self.frame,
            anchor=CENTER,
            width=500
        )

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
