from enum import Enum
from typing import Tuple



# type defs
User = Tuple[str, str, str]

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