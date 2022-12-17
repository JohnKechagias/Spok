from pathlib import Path

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from .placeholder_entry import PlaceholderEntry
from .auto_scrollbar import AutoScrollbar

from tktooltip import ToolTip
from tkinter import filedialog as fd



class EmailCreator(ttk.Frame):
    def __init__(
        self,
        master=None,
        subject='',
        body='',
        signature_path: Path = None,
        attachments_path: Path = None,
        *args,
        **kwargs
    ):
        super().__init__(master, padding=10)

        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)

        self.attachments_path = attachments_path

        self.signature = ''
        if signature_path is not None:
            try:
                with open(signature_path, 'r', encoding='UTF-8') as file:
                    self.signature = file.read()
            except Exception:
                pass

        self._subject = PlaceholderEntry(self, bootstyle=SECONDARY, placeholder='Subject', text=subject)
        self._subject.grid(row=0, column=0, columnspan=2, sticky=EW, pady=(0, 5))

        self._to = PlaceholderEntry(self, placeholder='To')

        self._body = ttk.Text(self, *args, **kwargs, undo=True)
        self._body.grid(row=1,  column=0, columnspan=2, sticky=NSEW, pady=5)
        self._body.insert(END, body.strip())

        self._body.bind('<KeyPress-t>', lambda _: self.get_email())

        self._columns = ('file', 'path')

        self._attachments = ttk.Treeview(
            self,
            bootstyle=SECONDARY,
            columns=self._columns,
            show=HEADINGS,
            *args,
            **kwargs
        )
        self._attachments.grid(row=2, column=0, sticky=NSEW)

        any(map(lambda i: self._attachments.heading(i, text=i.capitalize()),self._columns))
        self._attachments.bind('<Delete>', self._delete_selected_entries, add='+')

        self.scrollbar = AutoScrollbar(
            self,
            orient=VERTICAL,
            bootstyle=SECONDARY,
            command=self._attachments.yview
        )

        self._attachments.configure(yscroll=self.scrollbar.set)
        self.scrollbar.grid(row=2, column=1, sticky=NS)

        self.select_attachment_button = ttk.Button(
            master=self,
            bootstyle=(WARNING, OUTLINE),
            text='Attach File',
            command=self._select_attachment_file
        )
        self.select_attachment_button.grid(row=3, column=0, columnspan=2, pady=5, sticky=EW)
        msg = 'Attach file to email.'
        ToolTip(self.select_attachment_button, msg=msg, delay=1)

        self.get_attachments()

    def get_email(self) -> dict[str, str]:
        """ Return the email info in a form of a dict.
        Email info consists of the title, the recipient and the body of
        the email in HTML form. If the personalEmail flag is false, the
        recipient is empty.

            Returns:
                dict: email info
        """
        email = {}
        email['subject'] = self._subject.get()

        email['to'] = ''

        body = self._body.get('1.0', END)
        body = body.replace('\n', '<br>')
        body = '<html><head></head><body><p style="color:black">' + body +\
        self.signature + '</p></body></html>'

        email['body'] = body
        return email

    def get_subject(self) -> str:
        return self._subject.get()

    def get_body(self) -> str:
        return self._body.get('1.0', END)

    def get_attachments(self) -> list[str]:
        attachments = []
        for entry in self._attachments.get_children():
            path = self._attachments.item(entry, 'values')[1]
            attachments.append(path)

        return attachments

    def _select_attachment_file(self):
        attachment_path = fd.askopenfilename(
            title='Select attachment',
            filetypes=[("All files","*.*")],
            initialdir=self.attachments_path
        )

        if attachment_path not in {None, '', ()}:
            attachment_path = Path(attachment_path)
            filename = attachment_path.name
            self._add_entry([filename, attachment_path])

    def _add_entry(
        self,
        values: list[str],
        focus: bool = False
    ) -> str:
        """ Insert an item to the tree.

        Args:
            index: The entrys Tree index.
            values: The entrys values.
            tags: The entrys tags.
            focus: If true, the new entry will be focused.
            save_edit: If true, edit is saved.
        """
        entry = self._attachments.insert('', END, values=values)

        if focus:
            # Select entry
            self._clear_treeview_selection()
            self._attachments.selection_add(entry)

        return entry

    def _delete_selected_entries(self, event):
        try:
            entries_to_delete = self._attachments.selection()[0]
            self._attachments.delete(entries_to_delete)
        except:
            return
