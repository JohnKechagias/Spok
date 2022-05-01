from functools import  wraps

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from widgets.auto_scrollbar import AutoScrollbar



class DataViewer(ttk.Frame):
    """A custom 2D Ttk Treeview widget that displays a hierarchical collection of items.

    Each item has a textual label and an optional list of data values.
    The data values are displayed in successive columns
    after the tree label. Entries have 2 values, name and email.

    The treeview supports 3 types of entries:

    1. Entries without a 'flaggedEmail' or 'flaggedName' tag\n
    2. Entries with a 'flaggedEmail' tag\n
    3. Entries with a 'flaggedName' tag\n

    Each type of entry has a distinct background color.
    Entries are grouped together based on their tag and each group
    is shown in the order thats specified above."""

    def __init__(
        self,
        master=None,
        bootstyle=DEFAULT,
        *args,
        **kwargs,
    ):
        """Construct a Ttk Treeview with parent master.

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
        super().__init__(master)

        # make tree resizable
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        # define columns
        self._columns = ('index', 'name', 'email')
        # used to track where the next valid item (without a tag) should be inserted
        self._curr_valid_index = 0
        # stacks that stores edits. (used in undo and redo)
        self.edit_stack = []
        # stack size
        self.stack_size = 25
        # stack index that points to the current edit
        self.stack_index = -1
        # true if we are editing a row
        self._edit_mode = False
        self._item_to_edit = None

        self._tree = ttk.Treeview(
            self,
            bootstyle=bootstyle,
            columns=self._columns,
            show=HEADINGS,
            *args,
            **kwargs)
        self._tree.grid(row=0, column=0, sticky=NSEW)

        self._tree.tag_configure('flaggedEmail', background='#CA9242', foreground='white')
        self._tree.tag_configure('flaggedName', background='#ca5f42', foreground='white')

        # define and tweak columns
        self._tree.column("# 1", stretch=NO, width=45)
        self._tree.heading('index', text='Index')
        self._tree.heading('name', text='Name')
        self._tree.heading('email', text='Email')

        # setup scrollbar
        self.scrollbar = AutoScrollbar(
            self,
            orient=VERTICAL,
            command=self._tree.yview)

        self._tree.configure(yscroll=self.scrollbar.set)
        self.scrollbar.grid(row=0, column=1, sticky=NS)

        self._edit_name = ttk.StringVar()
        self._edit_email = ttk.StringVar()

        self._edit_frame = ttk.Frame(self._tree)
        self._edit_frame.columnconfigure(0, weight=1)
        self._edit_frame.columnconfigure(1, weight=1)

        self._edit_name_entry = ttk.Entry(self._edit_frame, textvariable=self._edit_name)
        self._edit_name_entry.grid(row=0, column=0, sticky=EW)

        self._edit_email_entry = ttk.Entry(self._edit_frame, textvariable=self._edit_email)
        self._edit_email_entry.grid(row=0, column=1, sticky=EW)

        self._tree.bind('<<TreeviewSelect>>', self._item_selected, add='+')
        self._tree.bind('<Double-Button-1>', self._enter_edit_mode, add='+')
        self.bind_all('<space>', self.create_entry, add='+')
        self.bind_all('<Escape>', self._cancel_edit_mode, add='+')
        self.bind_all('<Return>', self._leave_edit_mode, add='+')
        self.bind_all('<Button-3>', self._leave_edit_mode, add='+')
        self.bind_all('<Delete>', self._delete_selected_entry, add='+')
        self.bind_all('<Control-z>', self._undo, add='+')
        self.bind_all('<u>', self._redo, add='+')

    def _notOnEditMode(func):
        @wraps(func)
        def wrapperFunc(self, *args, **kwargs):
            if not self._edit_mode:
                return func(self, *args, **kwargs)
        return wrapperFunc

    def load_list(self, item_list:list):
        for item in item_list:
            self.insert_entry(values=item, save_edit=False)
        # select top entry
        self._clear_treeview_selection()
        self._tree.selection_add(self._tree.get_children()[0])

    @notOnEditMode
    def insert_entry(
        self,
        index:int=END,
        values:list=None,
        tags:list|tuple=None,
        focus:bool=False,
        save_edit=True
        ) -> str:
        """insert an item.

        POSSIBLE TAGS

        flaggedEmail, flaggedName
        """
        # default initialize values
        if values is None:
            values = ['', '']

        if index is END:
            item_index = len(self._tree.get_children()) + 1
            values.insert(0, item_index)
        else:
            values.insert(0, index + 1)

        if tags is not None and len(tags) > 0:
            entry = self._tree.insert('', index, values=values, tags=tags)
        else:
            self._curr_valid_index += 1
            entry = self._tree.insert('', index, values=values)

        if save_edit:
            self._push_edit(['insert', entry, index, values, tags])

        if focus:
            # select entry
            self._clear_treeview_selection()
            self._tree.selection_add(entry)

        # recalculate entries indexes if entry wasn't inserted in the end
        if index != END or index != item_index - 1:
            self._recalculate_indexes()

        return entry

    def create_entry(self, event:tk.Event=None):
        """create a new treeview entry and add it just before the
        entries with a tag"""
        self.insert_entry(self._curr_valid_index, focus=True)

    def _delete_selected_entry(self, event:tk.Event=None):
        try:
            entry_to_delete = self._tree.selection()[0]
        except:
            return
        self.delete_entry(entry_to_delete)

    @_notOnEditMode
    def delete_entry(self, entry:str, save_edit=True):
        # get item index in the tree
        index = int(self._tree.item(entry, 'values')[0]) - 1

        if self._tree.item(entry, 'tags') == '':
            self._curr_valid_index -= 1

        if save_edit:
            values = self._tree.item(entry, 'values')
            tags = self._tree.item(entry, 'tags')
            self._push_edit(['delete', entry, index, values, tags])

        self._tree.delete(entry)
        self._recalculate_indexes()

        # select the item with the same index as the one we deleted
        # ex. if we deleted item with index 42 select the new item with
        # index 42
        items = self._tree.get_children()
        num_of_items = len(items)

        if num_of_items == 0:
            return
        elif num_of_items == index:
            index -= 1

        temp = self._tree.get_children()[index]
        self._tree.selection_add(temp)

    def edit_entry(self, entry, values:tuple, save_edit=True):
        old_values = self._tree.item(entry, 'values')
        new_values = (old_values[0], values[0], values[1])
        if save_edit:
            self._push_edit(['edit', entry, old_values, new_values])
        self._tree.item(entry, values=new_values)

    def _item_selected(self, event:tk.Event=None):
        pass

    def _enter_edit_mode(self, event:tk.Event=None):
        self._edit_mode = True
        self._item_to_edit = self._tree.selection()[0]
        user = self._tree.item(self._item_to_edit)['values']
        self._edit_name.set(user[1])
        self._edit_email.set(user[2])
        self._edit_frame.place(relwidth=0.9, anchor=CENTER, relx=0.5, rely=0.5)

    def _leave_edit_mode(self, event:tk.Event=None):
        """Save changes and leave edit mode"""
        if not self._edit_mode: return
        new_values = (self._edit_name.get(), self._edit_email.get())
        self.edit_entry(self._item_to_edit, new_values)
        self._edit_mode = False
        self._edit_frame.place_forget()

    def _cancel_edit_mode(self, event:tk.Event=None):
        """Leave edit mode without saving the changes"""
        if self._edit_mode:
            self._edit_mode = False
            self._edit_frame.place_forget()

    @_notOnEditMode
    def _undo(self, event:tk.Event=None):
        """undo the latest edit"""
        if self.stack_index < 0:
            return

        edit = self.edit_stack[self.stack_index]
        if edit[0] == 'insert':
            self.delete_entry(edit[1], save_edit=False)
        elif edit[0] == 'delete':
            values = list(edit[3])
            del values[0]  # remove entry index
            tags = edit[4]
            entry = self.insert_entry(edit[2], values, tags, save_edit=False)
            # because we insert a new entry, the entrys ID has
            # changed, so we need to update it
            edit[1] = entry
        elif edit[0] == 'edit':
            values = list(edit[2])
            values.pop(0)
            self.edit_entry(edit[1], values, save_edit=False)
        self.stack_index -= 1

    @_notOnEditMode
    def _redo(self, event:tk.Event=None):
        """redo the latest edit"""
        if self.stack_index == len(self.edit_stack) - 1 or self.stack_index < -1:
            return

        self.stack_index += 1
        edit = self.edit_stack[self.stack_index]
        if edit[0] == 'insert':
            values = list(edit[3])
            del values[0]  # remove entry index
            tags = edit[4]
            entry = self.insert_entry(edit[2], values, tags, save_edit=False)
            # because we insert a new entry, the entrys ID has
            # changed, so we need to update it
            edit[1] = entry
        elif edit[0] == 'delete':
            self.delete_entry(edit[1], save_edit=False)
        elif edit[0] == 'edit':
            values = list(edit[3])
            del values[0]
            self.edit_entry(edit[1], values, save_edit=False)

    def _push_edit(self, edit:list):
        self.edit_stack.insert(self.stack_index + 1, edit)
        if self.stack_size < len(self.edit_stack):
            self._delete_oldest_edit()
        else:
            self.stack_index += 1

    def _delete_oldest_edit(self):
        if self.stack_size - (self.stack_index + 1) >=\
            (self.stack_index + 1):
            del self.edit_stack[-1]
            # update editStack index
            self.stack_index += 1
        elif self.stack_size - (self.stack_index + 1) <\
            (self.stack_index + 1):
            del self.edit_stack[0]

    def _recalculate_indexes(self):
        for index, item in enumerate(self._tree.get_children()):
            new_item_values = self._tree.item(item)['values']
            new_item_values[0] = index + 1
            self._tree.item(item, values=new_item_values)

    def _clear_treeview_selection(self):
        for i in self._tree.selection():
            self._tree.selection_remove(i)

    def _reset(self):
        items = self._tree.get_children()

        if len(items) != 0:
            self._tree.delete(*items)
        self._curr_valid_index = 0
        self.edit_stack = []
        self._cancel_edit_mode()
