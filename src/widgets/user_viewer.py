import tkinter as tk
from ttkbootstrap.constants import *

from .constants import Style
from .data_viewer import DataViewer



class UserViewer(DataViewer):
    """ A custom 2D Ttk Treeview widget that displays a hierarchical
    collection of items.

    Each item has a textual label and an optional list of data values.
    The data values are displayed in successive columns
    after the tree label. Entries have 2 values, name and email.

    The treeview supports 3 types of entries:

    1. Entries without a 'flaggedEmail' or 'flaggedName' tag
    2. Entries with a 'flaggedEmail' tag
    3. Entries with a 'flaggedName' tag

    Each type of entry has a distinct background color.
    Entries are grouped together based on their tag and each group
    is shown in the order thats specified above.
    """
    def __init__(
        self,
        master: tk.Widget = None,
        bootstyle: Style = DEFAULT,
        scrollbar_bootstyle: Style = DEFAULT,
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
        super().__init__(
            master,
            bootstyle=bootstyle,
            scrollbar_bootstyle=scrollbar_bootstyle,
            columns=('name', 'email'),
            indexing=True,
            *args,
            **kwargs
        )

        # The Email (based on the entry) was sent successfully
        self._tree.tag_configure(
            'emailSuccess',
            background='#00ff77',
            foreground='white'
        )
        # There was an error while sending the Email
        # (based on the entry).
        # Most probable cause is that the email was invalid
        self._tree.tag_configure(
            'emailError',
            background='#dd0101',
            foreground='white'
        )
