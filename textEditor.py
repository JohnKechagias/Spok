import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk



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
            self._vbar = ttk.Scrollbar(
                master=self,
                bootstyle=bootstyle,
                command=self._scrollBoth,
                orient=VERTICAL,
            )
            self._vbar.grid(row=0, rowspan=2, column=2, sticky=NS)
            self._numberedText.configure(yscrollcommand=self._updateScroll)
            self._text.configure(yscrollcommand=self._updateScroll)

        if hbar is not None:
            self._hbar = ttk.Scrollbar(
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
        self._findText = ttk.StringVar(self, value='Find..')
        self._findFrame = ttk.Frame(self._text)

        self._findEntry = tk.Entry(
            self._findFrame,
            autostyle=False,
            font=findFont,
            borderwidth=0,
            insertwidth=2,
            highlightthickness=0,
            background=findBackground,
            foreground=textFontColor,
            insertbackground=cursorColor,
            textvariable=self._findText)
        self._findEntry.pack(side=LEFT, pady=2, padx=(10, 8))

        #Import the image using PhotoImage function
        self._findButtonImg= ttk.PhotoImage(file='assets/x3.png')

        self._findCloseButton = tk.Button(
            self._findFrame,
            autostyle=False,
            image=self._findButtonImg,
            borderwidth=0,
            highlightthickness=0,
            background=darkBackgroundColor,
            activebackground=lighterDarkBackgroundColor,
            relief=FLAT)
        self._findCloseButton.pack(side=LEFT, expand=NO, pady=2, padx=(0, 6))

        self._text.bind_all('<Control-KeyPress-f>', self._openSearch, add='+')
        self._text.bind_all('<Escape>', self._closeSearch, add='+')

    def loadFile(self, path:str):
        self.reset()
        with open(path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for row in lines:
                self._text.insert(END, row)

    def _openSearch(self, event):
        self._findFrame.place(relx=1, rely=0, anchor=NE, bordermode=OUTSIDE)
        self._isSearchOpen = True

    def _closeSearch(self, event):
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
        super().__init__(width=width, *args, **kwargs)
        # move every index to the right of the line
        self.tag_configure('tag_right', justify=RIGHT)
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
            self.insert(END, f'{i + 1}  \n', 'tag_right')

        # remove empty line thats constanlty added by the text widget
        if self.get('end-1c', END) == '\n':
            self.delete('end-1c', END)