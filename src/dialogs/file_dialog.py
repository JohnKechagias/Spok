from pathlib import Path
import subprocess
import sys
import os



def open_folder(path: Path) -> None:
    """ Platform independent func to open a folder in the default
    folder dialog.

    Args:
        path: Folder path.
    """
    if sys.platform == 'darwin':
        subprocess.check_call(['open', path])
    elif sys.platform == 'linux2' or sys.platform == 'linux':
        subprocess.check_call(['xdg-open', path])
    elif sys.platform == 'win32':
        os.startfile(path)
