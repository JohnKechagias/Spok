from enum import Enum
from ttkbootstrap.themes.standard import STANDARD_THEMES



# Type defs
ID = str
User = tuple[str, str, str]
RGB = tuple[int, int, int]
Hex = str

# Ulist (userslist) is a custom list where each row represents a user.
# Row: [name, email, errorflags_string].
Ulist = list[list[str]]

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
BG = 'bg'
FG = 'fg'

# Theme typdefs
Style = str | tuple[str, ...] | list[str]
