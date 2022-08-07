from enum import Enum
from typing import Tuple, List
from ttkbootstrap.themes.standard import STANDARD_THEMES



# Type defs
User = Tuple[str, str, str]
Color = Tuple[int, int, int]
Hex = str

# Ulist (userslist) is a custom list where each row represents a user.
# Row: [name, email, errorflags_string].
Ulist = List[List[str]]

# Logging level enum
class LogLevel(Enum):
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4
    SUCCESS = 5

# Positional constants
LEFT = 'left'
MIDDLE = 'middle'
RIGHT = 'right'

# Theme constants
THEMENAME = 'darkly'
THEME = STANDARD_THEMES['darkly']['colors']
