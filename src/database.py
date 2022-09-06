import sqlite3
from pathlib import Path
from sqlite3 import Error
from ttkbootstrap import font
from typing import Any, List, Optional, Union

from widgets.constants import Hex



sql_command = str

create_users_table = """ 
    CREATE TABLE IF NOT EXISTS users(
        email TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        begin_date TEXT,
        end_date TEXT
    );
"""

create_fonts_table = """
    CREATE TABLE IF NOT EXISTS fonts(
        name TEXT PRIMARY KEY,
        family TEXT NOT NULL,
        size TINYINT NOT NULL,
        color TEXT NOT NULL,
        weight TEXT NOT NULL,
        slant TEXT NOT NULL,
        underline BOOLEAN NOT NULL,
        overstrike BOOLEAN NOT NULL
    );
"""

create_tables_commands = (
    create_fonts_table,
    create_users_table
)

class Database:
    _conn = None
   
    @classmethod 
    def connect(cls, db_file: Path) -> sqlite3.Connection:
        """ Create a database connection to a SQLite database. """
        conn = None
        try:
            conn = sqlite3.connect(db_file)
        except Error as e:
            print(e)

        cls._conn = conn

    @classmethod
    def execute(
        cls, 
        command: sql_command,
        parameters: Optional[Union[Any, List[Any]]] = None
    ):
        """ Create a database table.
        
        Args:
            conn: Connection object.
            command: A sql command.
            parameters: Command parameters.
        """
        try:
            cursor = cls._conn.cursor()
            if parameters is None:
                cursor.execute(command)
            else:
                cursor.execute(command, parameters)
        except Error as e:
            print(e)
        
        return cursor

    def _create_tables(cls):
        for command in create_tables_commands:
            cls.execute(command)

    def add_font(
        cls,
        name: str,
        font: font.Font,
        color: Hex
    ):
        ...
    def get_font(cls, name: str): ...
    def get_fonts(cls) -> List[font.Font]: ...
