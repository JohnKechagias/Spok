from pathlib import Path
import ttkbootstrap as ttk
import os

from database import Database



ICONS = []

def load_assets(assets_path: Path):
    """ Load app assets.

    Args:
        assets_pathL: Path to assets folder.
    """
    load_icons(assets_path / 'icons')


def load_icons(icons_path: Path):
    """ Loads icons assets. The name of a loaded icon is its
    base filename, if we replace `_` with `-` and remove the
    icon dimension, ex. `_32px` and the file extension.

    ex. `default_icon_32px.png` is converted to `default-icon`.

    Args:
        icons_path: Path to icons folder.
    """
    files = os.listdir(icons_path)

    for icon in files:
        name = icon.rsplit('.', 1)[0]
        # remove icon dimension
        if 'px' in name.rsplit('_', 1)[-1]:
            name = name.rsplit('_', 1)[0]
        name = name.replace('_', '-')

        path = icons_path / icon
        ICONS.append(ttk.PhotoImage(name=name, file=path))
