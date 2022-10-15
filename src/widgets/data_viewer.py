from functools import  wraps

import tkinter as tk
from tkinter.tix import CELL
from typing import  Any, Callable, Union
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from .constants import *
from .auto_scrollbar import AutoScrollbar



class DataViewer(ttk.Frame):
    """ A custom 2D Ttk Treeview widget that displays a hierarchical
    collection of items.

    Each item has a textual label and an optional list of data values.
    The data values are displayed in successive columns
    after the tree label.
    """
    def __init__(
        self,
        master: tk.Widget = None,
        bootstyle: Style = DEFAULT,
        scrollbar_bootstyle: Style = DEFAULT,
        columns: tuple[str, ...] | list[str] = None,
        indexing: bool = True,
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
        super().__init__(master)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.indexing = indexing
        self.columns = list(columns)
        if self.indexing: self.columns.insert(0, 'index')
        # Used to track where the next valid item (without a tag) should be inserted
        self._curr_valid_index = 0
        # Stacks that stores edits. (used in undo and redo)
        self.edit_stack = []
        # Stack size
        self.stack_size = 25
        # Stack index that points to the current edit
        self.stack_index = -1
        # True if we are editing a row
        self._edit_mode = False
        self._item_to_edit = None

        self._tree = ttk.Treeview(
            self,
            bootstyle=bootstyle,
            columns=self.columns,
            show=HEADINGS,
            *args,
            **kwargs
        )
        self._tree.grid(row=0, column=0, sticky=NSEW)

        # Define and tweak columns
        if indexing: self._tree.column('index', stretch=NO, width=45)

        any(map(lambda i: self._tree.heading(i, text=i.capitalize()), columns))

        # Setup scrollbar
        self.scrollbar = AutoScrollbar(
            self,
            orient=VERTICAL,
            bootstyle=scrollbar_bootstyle,
            command=self._tree.yview
        )

        self._tree.configure(yscroll=self.scrollbar.set)
        self.scrollbar.grid(row=0, column=1, sticky=NS)

        self._tree.bind('<Double-Button-1>', self._on_double_button_1, add='+')
        self._tree.bind('<<TreeviewSelect>>', self._item_selected, add='+')
        self._tree.bind('<Delete>', self._delete_selected_entries, add='+')
        self._tree.bind('<space>', self.create_entry, add='+')
        self._tree.bind('<Control-z>', self._undo, add='+')
        self._tree.bind('<u>', self._redo, add='+')

    def _notOnEditMode(func: Callable[[Any], Any]):
        @wraps(func)
        def wrapperFunc(self, *args, **kwargs):
            if not self._edit_mode:
                return func(self, *args, **kwargs)
        return wrapperFunc

    def load_list(self, item_list: list[str]):
        self.reset()
        any(map(self.add_entry, item_list))
        # Select top entry
        self._tree.selection_add(self._tree.get_children()[0])

    def get_list_of_valid_entries(self) -> list[User]:
        values = []
        for entry in self._tree.get_children():
            entry_tags = self._tree.item(entry, 'tags')
            # Export only entry that don't have a tag
            if len(entry_tags) == 0 or entry_tags is None:
                entry_values = self._tree.item(entry, 'values')
                values.append(entry_values)
        return values

    def get_num_of_valid_entries(self, num: int) -> list[User]:
        values = []
        for entry in self._tree.get_children()[:num]:
            entry_tags = self._tree.item(entry, 'tags')
            # Export only entry that don't have a tag
            if len(entry_tags) == 0 or entry_tags is None:
                entry_values = self._tree.item(entry, 'values')
                values.append(entry_values)
        return values

    def get_entry_from_index(self, index: int) -> User:
        return self._tree.get_children()[index - 1]

    @_notOnEditMode
    def insert_entry(
        self,
        index: Union[int, END] = END,
        values: list[str] | None = None,
        tags: list[str] | tuple[str, ...] | None = None,
        focus: bool | None = False,
        save_edit: bool | None = True
    ) -> str:
        """ Insert an item to the tree.

        Args:
            index: The entrys Tree index.
            values: The entrys values.
            tags: The entrys tags.
            focus: If true, the new entry will be focused.
            save_edit: If true, edit is saved.
        """
        # Default initialize values
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
            # Select entry
            self._clear_treeview_selection()
            self._tree.selection_add(entry)

        # Recalculate entries indexes if entry wasn't inserted in the end
        if index != END or index != item_index - 1:
            self._recalculate_indexes()
        return entry

    @_notOnEditMode
    def add_entry(
        self,
        values: list[str] | None = None,
        tags: list[str] | tuple[str, ...] | None = None,
    ) -> str:
        self.insert_entry(END, values, tags, False, False)

    def create_entry(self, event: tk.Event | None = None):
        """ Create a new treeview entry and add it just before the
        entries with a tag. """
        self.insert_entry(self._curr_valid_index, focus=True)

    @_notOnEditMode
    def delete_entries(
        self,
        entry: ID,
        save_edit: bool = True
    ) -> None:
        # Get item index in the tree
        index = int(self._tree.item(entry, 'values')[0]) - 1

        if self._tree.item(entry, 'tags') == '':
            self._curr_valid_index -= 1

        if save_edit:
            values = self._tree.item(entry, 'values')
            tags = self._tree.item(entry, 'tags')
            self._push_edit(['delete', entry, index, values, tags])

        self._tree.delete(entry)
        self._recalculate_indexes()

        # Select the item with the same index as the one we deleted
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

    def edit_entry(
        self,
        entry: ID,
        new_value: str,
        cell_column_index: int,
        save_edit: bool = True
    ) -> None:
        """ Change entrys values.

        Args:
            entry: The entrys id to be modified.
            new_value: The entries new cell value.
            cell_column_index: The cells to be modified column index.
            save_edit: If true, edit is saved.
        """
        new_values = self._tree.item(entry)['values']
        old_value = new_values[cell_column_index]
        new_values[cell_column_index] = new_value

        # TODO might want to also save the tags
        if save_edit:
            self._push_edit([
                'edit',
                entry,
                old_value,
                new_value,
                cell_column_index
            ])
        self._tree.item(entry, values=new_values)

        # Remove entrys error tags if the new value are
        # different from the old one. We consider the
        # entry fixed.
        if old_value != new_value:
            self._tree.item(entry, tags=[])

    def _delete_selected_entries(self, event: tk.Event):
        try:
            entries_to_delete = self._tree.selection()
        except:
            return
        self.delete_entries(entries_to_delete)

    def _item_selected(self, event: tk.Event = None):
        pass

    def _on_double_button_1(self, event: tk.Event | None = None):
        """ Callback for when the Button-1 is double clicked.
        Create a cell entry above the double clicked cell and
        use it to edit the cells value. """
        # Check if the user clicked a cell
        if self._tree.identify_region(event.x, event.y) != CELL:
            return

        # Check if any entry is selected
        try:
            entry = self._tree.selection()[0]
        except IndexError: return

        column = self._tree.identify_column(event.x)
        # Column index, '#1' will become 0
        column_index = int(column[1:]) - 1

        # If the column clicked is the entry cell, don't do anything
        if self.indexing and column_index == 0: return

        cell_value = self._tree.item(entry)['values'][column_index]
        cell_bbox = self._tree.bbox(entry, column_index)

        edit_entry = tk.Entry(self, width=cell_bbox[2])
        edit_entry.place(
            x=cell_bbox[0],
            y=cell_bbox[1],
            width=cell_bbox[2],
            height=cell_bbox[3]
        )
        edit_entry.cell_column_index = column_index
        edit_entry.entry_id = entry
        edit_entry.insert(0, cell_value)
        edit_entry.select_range(0, END)
        edit_entry.focus()

        edit_entry.bind('<FocusOut>', self._on_focus_out)
        edit_entry.bind('<Escape>', self._on_focus_out)
        edit_entry.bind('<Return>', self._on_enter_pressed)

    def _on_focus_out(self, event: tk.Event):
        """ Callback for we focus out of a cell entry. """
        event.widget.destroy()

    def _on_enter_pressed(self, event: tk.Event):
        """ Callback for when the enter key is pressed. """
        entry: ttk.Entry = event.widget
        new_cell_value = entry.get()
        # If the new values are different from the old ones and the
        # entry has an error flag, remove the error flag (consider the
        # entry fixed).

        # 0 for #1, 1 for #2, etc..
        cell_column_index = entry.cell_column_index
        entry_id = entry.entry_id

        current_values = self._tree.item(entry_id)['values']
        current_values[cell_column_index] = new_cell_value

        self.edit_entry(entry_id, new_cell_value, cell_column_index)
        entry.destroy()

    @_notOnEditMode
    def _undo(self, event: tk.Event):
        """ Undo the latest edit. """
        if self.stack_index < 0:
            return

        edit = self.edit_stack[self.stack_index]
        if edit[0] == 'insert':
            self.delete_entries(edit[1], save_edit=False)
        elif edit[0] == 'delete':
            values = list(edit[3])
            del values[0]  # Remove entry index
            tags = edit[4]
            entry = self.insert_entry(edit[2], values, tags, save_edit=False)
            # Because we insert a new entry, the entrys ID has
            # changed, so we need to update it
            self._clear_treeview_selection()
            self._tree.selection_add(entry)
            edit[1] = entry
        elif edit[0] == 'edit':
            self.edit_entry(edit[1], edit[2], edit[4], save_edit=False)
        self.stack_index -= 1

    @_notOnEditMode
    def _redo(self, event: tk.Event):
        """ Redo the latest edit. """
        if self.stack_index == len(self.edit_stack) - 1 or self.stack_index < -1:
            return

        self.stack_index += 1
        edit = self.edit_stack[self.stack_index]
        if edit[0] == 'insert':
            values = list(edit[3])
            del values[0]  # remove entry index
            tags = edit[4]
            entry = self.insert_entry(edit[2], values, tags, save_edit=False)
            # Because we insert a new entry, the entrys ID has
            # changed, so we need to update it
            edit[1] = entry
        elif edit[0] == 'delete':
            self.delete_entries(edit[1], save_edit=False)
        elif edit[0] == 'edit':
            self.edit_entry(edit[1], edit[3], edit[4], save_edit=False)

    def _push_edit(self, edit: list[str]):
        self.edit_stack.insert(self.stack_index + 1, edit)
        if self.stack_size < len(self.edit_stack):
            self._delete_oldest_edit()
        else:
            self.stack_index += 1

    def _delete_oldest_edit(self):
        if self.stack_size - (self.stack_index + 1) >=\
            (self.stack_index + 1):
            del self.edit_stack[-1]
            # Update editStack index
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

    def reset(self):
        items = self._tree.get_children()

        if items := self._tree.get_children():
            self._tree.delete(*items)
        self._curr_valid_index = 0
        self.edit_stack = []
