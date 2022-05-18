import tkinter as tk
from ttkbootstrap.constants import *



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

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # Create a proxy for the underlying widget
        # self._w is the name of the widget (cText)
        # each time an event happens it is passed to a tcl command which has
        # the same name as the widget class (cText)

        # Rename the main tcl command (cText) to cText_orig
        # !!!ATTENTION!!!
        # We don't rename the var self._w, but the command thats named after self._w
        self._orig = self._w + '_orig'
        self.tk.call('rename', self._w, self._orig)
        # Create a proxy command and give it the same name as the one of the old
        #  command (cText), so that, when an event happens, the new proxy func is called.
        self.tk.createcommand(self._w, self._proxy)

    def _proxy(self, *args):
        # Pass the args to the original widget function
        result = None
        try:
            cmd = (self._orig,) + args
            result = self.tk.call(cmd)
        except tk.TclError:
            print(f'_tkinter.TclError. Command args: {args}')

        # Generate an event if something was added or deleted,
        # or the cursor position changed
        if (args[0] in ('insert', 'replace', 'delete') or
            args[0:3] == ('mark', 'set', 'insert') or
            args[0:2] == ('xview', 'moveto') or
            args[0:2] == ('xview', 'scroll') or
            args[0:2] == ('yview', 'moveto') or
            args[0:2] == ('yview', 'scroll')
        ):
            self.event_generate('<<TextChanged>>', when='tail')

        # Return what the actual widget returned
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

    def __init__(self, width=5, *args, **kwargs) -> None:
        super().__init__(width=width, state=DISABLED, *args, **kwargs)
        # Move every index to the right of the line
        self.tag_configure('tag_right', justify=RIGHT)
        self._num_of_lines = 0

    def set_num_of_lines(self, new_num_of_lines):
        if self._num_of_lines != new_num_of_lines:
            self._num_of_lines = new_num_of_lines
            self._recalculate_numbers()

    def _recalculate_numbers(self):
        self.configure(state=NORMAL)
        # Clear all indexes
        self.delete('1.0', END)
        # Recalculate all line indexes
        for i in range(self._num_of_lines):
            self.insert(END, f'{i + 1}  \n', 'tag_right')

        # Remove empty line thats constanlty added by the text widget
        if self.get('end-1c', END) == '\n':
            self.delete('end-1c', END)
        self.configure(state=DISABLED)
