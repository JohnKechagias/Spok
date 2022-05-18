from typing import List
import pandas as pd
import unicodedata
import re



def split_name_and_email(row: str) -> tuple[str, str]:
    """Strips the email from a text

    RETURNS

    (text without email, email)"""
    words = row.split()
    email = 'null'
    for index, word in enumerate(words):
        if ('@' in word):
            email = words.pop(index)
            break
    return (' '.join(words), email)


def remove_nonspacing_marks(s: str) -> str:
    "Decompose the unicode string s and remove non-spacing marks."
    return ''.join(c for c in unicodedata.normalize('NFKD', s)
                   if unicodedata.category(c) != 'Mn')


def txt_to_list(txtPath: str) -> list[tuple[str, str ,str]]:
    """Convert a txt file to a list. Each row in the txt must contain an email and a name.
    If an entry is missing a name or an email and logging is disabled, it will be deleted

    Entries that are missing a name or an email will be deleted.
    TIF loggin is enabled entries will be checked for duplicate emails and names.

    If duplicates are found, each entry with a duplicate will be marked with an error
    Flag and a number. The number will be the same for all entries with the same
    duplicates (is used as a common reference).


    ERROR FLAGS

    E: duplicate email,
    N: duplicate name

    TXT FORMAT

    each row must have an email and a name

    RETURNS

    a list where each entry is [email, name, errorFlag]"""

    try:
        # Read from attendants
        with open(txtPath, "r", encoding='utf-8') as file:
            lines = file.readlines()
    except IOError:
        print("Could not find txt file.")

    users_list = []
    for line in lines:
        # Remove tabs, whitespaces and newlines
        line = line.replace('\n', '').replace('\t', ' ').replace('-', ' ').strip()
        # Continue if line is empty
        if line == '': continue
        line = re.sub(' +', ' ', line)

        name, email = split_name_and_email(line)
        users_list.append((name, email))

    users_list = clean_name_email_list(users_list)
    return users_list


def exel_to_list(path: str) -> list[tuple[str, str ,str]]:
    df = pd.read_excel(
        path,
        usecols=['Email', 'Name'],
        names=['Timestamp', 'Email', 'Name']
    )[['Name', 'Email']]
    return dataframe_to_list(df)


def csv_to_list(path: str) -> list[tuple[str, str ,str]]:
    df = pd.read_csv(
        path,
        usecols=['Email', 'Name'],
        names=['Timestamp', 'Email', 'Name']
    )[['Name', 'Email']]
    return dataframe_to_list(df)


def dataframe_to_list(df: pd.DataFrame) -> list[tuple[str, str ,str]]:
    df.drop_duplicates(subset=None, keep='first', inplace=True)
    df.sort_values(by=['Name'], inplace=True)
    df.reset_index(drop=True, inplace=True)
    user_list = df.values.tolist()
    user_list = clean_name_email_list(user_list)
    return user_list


def list_to_txt(list: list) -> None:
    with open('userlist.temp', 'w', encoding='utf-8') as file:
        for item in list:
            file.write(f'{item[2]} | {item[0]} {item[1]}\n')


def clean_name_email_list(
    user_list: list[list[str]],
    check_for_name_duplicates=True,
    check_for_email_duplicates=False
    ) -> list[list[str, str, str]]:
    flag_error_index = 0
    # True if the the exact item is already in the list
    duplicate = False
    clean_user_list = []

    for user in user_list:
        name = clean_name(user[0])
        email = clean_email(user[1])

        flags = ''
        if name == '' or email == '':
            continue

        # Check if the user name or user email already exists in the list
        for user in clean_user_list:
            if name == user[0] and email == user[1]:
                duplicate = True
                break

            if check_for_name_duplicates and name == user[0]:
                flags = flags.join(f'-E{flag_error_index}')
                user[2] = user[2].join(f'-E{flag_error_index}')
                flag_error_index += 1

            elif check_for_email_duplicates and email == user[1]:
                flags = flags.join(f'-N{flag_error_index}')
                user[2] = user[2].join(f'-N{flag_error_index}')
                flag_error_index += 1

        if not duplicate:
            clean_user_list.append([name, email, flags])
        duplicate = False

    for user in clean_user_list:
        user[2] = user[2].removeprefix('-')

    # Sort list based on the name
    clean_user_list = sorted(clean_user_list, key=lambda a: a[0])
    return clean_user_list


def clean_name(name: str) -> str:
    name = name.translate(str.maketrans('', '', ')(!\'\":@#$.,')).upper()
    name = name.replace('\n', '').replace('\t', ' ').replace('-', ' ').strip()
    name = remove_nonspacing_marks(name)
    name = re.sub(' +', ' ', name)
    return name


def clean_email(email: str)-> str:
    email = email.translate(str.maketrans('', '', ')(\'\"')).strip()
    return email


if __name__ == '__main__':
    exel_to_list('test.xlsx')