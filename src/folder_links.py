from pathlib import Path
import ttkbootstrap as ttk
from functools import partial
from ttkbootstrap.constants import *

from widgets.image_button import ImageButton
from dialogs.file_dialog import open_folder
from tktooltip import ToolTip
from widgets.constants import *



class FolderLinks(ttk.Frame):
    def __init__(self, master, folders: list[Path], *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.buttons = {}

        for path in folders:
            folder_name = path.name
            self.buttons[path.name] = ImageButton(
                master=self,
                default_image=f'{folder_name}-folder-default',
                active_image=f'{folder_name}-folder-active',
                background=THEME[BG],
                command=partial(open_folder, path)
            )
            self.buttons[path.name].pack(side=LEFT, expand=TRUE, padx=10)
            ToolTip( self.buttons[path.name], msg=f"{folder_name.replace('-', ' ')} folder", delay=1)
