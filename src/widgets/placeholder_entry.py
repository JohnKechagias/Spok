import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *



class PlaceholderEntry(ttk.Entry):
    def __init__(
        self,
        master=None,
        placeholder: str ='placeholder',
        placeholdercolor: str ='gray',
        text: str | None = None,
        *args,
        **kwargs
    ) -> None:
        super().__init__(master, *args, **kwargs)

        self.placeholder = placeholder
        self.placeholder_color = placeholdercolor
        self.foreground_color = self['foreground']

        self.bind("<FocusIn>", lambda _: self.focus_in())
        self.bind("<FocusOut>", lambda _: self.focus_out())

        if not self.get() and not text:
            self.insert_placeholder()
        elif text:
            self.insert(END, text)

    def insert_placeholder(self):
        self.insert(0, self.placeholder)
        self['foreground'] = self.placeholder_color

    def focus_in(self):
        if str(self['foreground']) == self.placeholder_color:
            self.clean_placeholder()

    def clean_placeholder(self):
        self.delete('0', END)
        self['foreground'] = self.foreground_color

    def focus_out(self):
        if not self.get():
            self.insert_placeholder()


class tkPlaceholderEntry(tk.Entry):
    def __init__(
        self,
        master=None,
        placeholder: str ='placeholder',
        placeholdercolor: str ='gray',
        text: str | None = None,
        *args,
        **kwargs
    ) -> None:
        super().__init__(master, *args, **kwargs)

        self.placeholder = placeholder
        self.placeholder_color = placeholdercolor
        self.foreground_color = self['foreground']

        self.bind("<FocusIn>", self.focus_in)
        self.bind("<FocusOut>", self.focus_out)

        if not self.get() and not text:
            self.insert_placeholder()
        else:
            self.insert(END, text)

    def insert_placeholder(self):
        self.insert(0, self.placeholder)
        self['foreground'] = self.placeholder_color

    def focus_in(self, _):
        if str(self['foreground']) == self.placeholder_color:
            self.clean_placeholder()

    def clean_placeholder(self):
        self.delete('0', END)
        self['foreground'] = self.foreground_color

    def focus_out(self, _):
        if not self.get():
            self.insert_placeholder()
