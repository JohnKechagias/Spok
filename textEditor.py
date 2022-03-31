import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk

class TextEditor(ttk.Frame):

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

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(1, weight=1)

        # setup text widget
        self._numberedText = NumberedText(master=self)
        self._text = CText(master=self, wrap=WORD, **kwargs)
        self._hbar = None
        self._vbar = None

        self._numberedText.grid(row=0, column=0, sticky=NS)
        self._text.grid(row=0, column=1, sticky=NSEW)

        # delegate text methods to frame
        for method in vars(ttk.Text).keys():
            if any(['pack' in method, 'grid' in method, 'place' in method]):
                pass
            else:
                setattr(self, method, getattr(self._text, method))

        # setup scrollbars
        if vbar:
            self._vbar = ttk.Scrollbar(
                master=self,
                bootstyle=bootstyle,
                command=self._scrollBoth,
                orient=VERTICAL,
            )
            self._vbar.grid(row=0, column=2, sticky=NS)
            self._numberedText.configure(yscrollcommand=self._updateScroll)
            self._text.configure(yscrollcommand=self._updateScroll)

        if hbar:
            self._hbar = ttk.Scrollbar(
                master=self,
                bootstyle=bootstyle,
                command=self._text.xview,
                orient=HORIZONTAL,
            )
            self._hbar.grid(row=1, column=0, columnspan=3, sticky=EW)
            self._text.configure(xscrollcommand=self._hbar.set)

        # position scrollbars
        if self._hbar:
            self.update_idletasks()
            self._text_width = self.winfo_reqwidth()
            self._scroll_width = self.winfo_reqwidth()

        self._text.bind('<<TextChanged>>', self._onChange)

        if autohide:
            self.autohide_scrollbar()
            self.hide_scrollbars()

    def _onChange(self, *_):
        newNumOfLines = self._text.count('1.0', END, 'displaylines')[0]
        self._numberedText.setNumOfLines(newNumOfLines)

    
    def _scrollBoth(self, action, position, type=None):
        self._text.yview_moveto(position)
        self._numberedText.yview_moveto(position)

    def _updateScroll(self, first, last, type=None):
        self._text.yview_moveto(first)
        self._numberedText.yview_moveto(first)
        self._vbar.set(first, last)

    def _combinedVerticalCallback(self, *args):
            self._text.yview(*args)
            self._numberedText.yview(*args)


class CText(ttk.Text):
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
        cmd = (self._orig,) + args
        result = self.tk.call(cmd)

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
        

class NumberedText(ttk.Text):
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
    
    def __init__(self, width=3, *args, **kwargs):
        super().__init__(width=width, border=0, *args, **kwargs)
        # move every index to the right of the line
        self.tag_configure('tag_right', justify=RIGHT)
        self.tag_configure('tag_selected', background='white')
        self._numOfLines = 0

    def setNumOfLines(self, newNumOfLines):
        if self._numOfLines != newNumOfLines:
            self._numOfLines = newNumOfLines
            self._recalculateNumbers()

    def _recalculateNumbers(self):
        # clear all indexes
        self.delete('1.0', END)
        # recalculate all line indexes
        for i in range(self._numOfLines):
            self.insert(f'{i + 1}.0', f'{i + 1}\n', 'tag_right')