import ttkbootstrap as ttk
from ttkbootstrap.constants import *

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
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        # setup text widget
        self._numberedText = ttk.Text(master=self, width=3)
        self._numberedText.tag_configure('line', justify=RIGHT)
        self._text = cText(master=self, wrap=WORD, **kwargs)
        self._hbar = None
        self._vbar = None

        self._numOfTextLines = 0

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
            self._vbar.grid(row=0, column=2, sticky=NSEW)
            self._numberedText.configure(yscrollcommand=self._updateScroll)
            self._text.configure(yscrollcommand=self._updateScroll)

        if hbar:
            self._hbar = ttk.Scrollbar(
                master=self,
                bootstyle=bootstyle,
                command=self._text.xview,
                orient=HORIZONTAL,
            )
            self._hbar.grid(row=1, column=1, columnspan=3, sticky=NSEW)
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
        numberOfTextLines = self._text.count('1.0', END, 'displaylines')[0]

        if numberOfTextLines != self._numOfTextLines:
            self._numOfTextLines = numberOfTextLines
            self._numberedText.delete('1.0', END)
            for i in range(numberOfTextLines):
                self._numberedText.insert(f'{i + 1}.0', f'{i + 1}\n')

    
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


class cText(ttk.Text):
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