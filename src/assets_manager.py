from pathlib import Path
import ttkbootstrap as ttk
import os



ICONS = []

def load_assets(assets_path: Path):
    files = os.listdir(assets_path)

    for icon in files:
        words = icon.rsplit('_', 1)
        # remove filetype from the last word
        words[-1] = words[-1].split('.')[0]
        words[0] = words[0].replace('_', '-')

        _path = assets_path / icon
        ICONS.append(ttk.PhotoImage(name=words[0], file=_path))
