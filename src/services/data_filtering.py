from pathlib import Path
from widgets.constants import *
import pandas as pd
import unicodedata



def file_to_ulist(path: Path) -> Ulist:
    """ Convert a datafile (exel, csv, ...) to a Ulist.
    File must include a `Name` and `Email` columns.

    Args:
        path: Path to datafile.

    Returns:
        The Ulist representation of the file.

    Raises:
        NotImplementedError: When the provided file isn't a datafile.
    """
    filetype = path.suffix[1:]

    if filetype in {'exel', 'xls', 'xlsx', 'xlsm',
        'xlsb', 'odf', 'ods', 'odt'}:
        return exel_to_list(path)
    elif filetype == 'csv':
        return csv_to_list(path)
    else:
        raise NotImplementedError('Can\'t get userlist from file. Filetype isn\'t supported.')


def exel_to_list(path: Path) -> Ulist:
    """ Convert an exel to a userlist. """
    df = pd.read_excel(
        path,
        usecols=["Email", "Name"],
    )[["Name", "Email"]]
    return dataframe_to_list(df)


def csv_to_list(path: Path) -> Ulist:
    """ Convert a csv to a userlist. """
    df = pd.read_csv(
        path,
        usecols=["Email", "Name"],
    )[["Name", "Email"]]
    return dataframe_to_list(df)


def dataframe_to_list(df: pd.DataFrame) -> Ulist:
    """ Convert a dataframe to a userlist. """
    df["Name"] = df["Name"].map(clean_name)
    df["Email"] = df["Email"].map(clean_email)
    df.dropna(inplace=True)
    df.drop_duplicates(keep="last", inplace=True)
    df.sort_values(by=["Name"], inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df.values.tolist()


def remove_nonspacing_marks(s: str) -> str:
    """ Decompose the unicode string `s` and remove non-spacing marks. """
    return "".join(c for c in unicodedata.normalize("NFKD", s)
                   if unicodedata.category(c) != "Mn")


def clean_name(name: str) -> str:
    """ Remove invalid chars from the name str. """
    name = name.translate(str.maketrans("-", " ", ")(!\"\":@#$,"))
    return remove_nonspacing_marks(name).upper().strip()


def clean_email(email: str) -> str:
    """ Remove invalid chars from the email str. """
    return email.translate(str.maketrans("", "", ")(\"\"")).strip()
