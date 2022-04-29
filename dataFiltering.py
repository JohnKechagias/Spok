import numpy as np
import pandas as pd
import unicodedata
import unidecode
import re
from itertools import permutations



def split_name_and_email(row:str) -> tuple:
    """Strips the email from a text

    RETURNS

    (text without email, email)"""
    words = row.split()
    email = ''
    for index, word in enumerate(words):
        if ('@' in word):
            email = words.pop(index)
            break
    return (words, email)

def remove_nonspacing_marks(s):
    "Decompose the unicode string s and remove non-spacing marks."
    return ''.join(c for c in unicodedata.normalize('NFKD', s)
                   if unicodedata.category(c) != 'Mn')

def txt_to_list(txtPath:str, logging=False) -> None:
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
        # read from attendants
        with open(txtPath, "r", encoding='utf-8') as file:
            lines = file.readlines()
    except IOError:
        print("Could not find txt file.")

    for i, line in enumerate(lines):
        # remove tabs, whitespaces and newlines
        lines[i] = re.sub(" +", " ", line.replace('\n', '').replace('\t', ' ').replace('-', ' ').strip())

    # remove empty lines
    lines = filter(lambda a : a != '', lines)

    user_list = []
    flag_error_index = 0
    # true if the the exact item is already in the list
    duplicate = False

    for line in lines:
        name, email = split_name_and_email(line)

        flags = ''
        if name == '' or email == '':
            continue

        # filter name
        filtered_name_list = []
        for word in name:
            temp = word.translate(str.maketrans('', '', ')(!\'\":@#$.,')).upper()
            temp = remove_nonspacing_marks(temp)
            filtered_name_list.append(temp)

        # filter email
        filtered_email = email.translate(str.maketrans('', '', ')(\'\"'))
        filtered_name  = ' '.join(filtered_name_list)

        # check if the user name or user email already exists in the list
        for user in user_list:
            if filtered_email == user[0] and filtered_name == user[1]:
                duplicate = True

            if filtered_email == user[0]:
                flags = flags.join(f'-N{flag_error_index}')
                user[2] = user[2].join(f'-N{flag_error_index}')
                flag_error_index += 1
            if filtered_name == user[1]:
                flags = flags.join(f'-E{flag_error_index}')
                user[2] = user[2].join(f'-E{flag_error_index}')
                flag_error_index += 1

        if not duplicate:
            user_list.append([filtered_email, filtered_name, flags])
        duplicate = False

    for user in user_list:
        user[2] = user[2].removeprefix('-')

    return user_list

def list_to_txt(list:list):
    with open('cleanFile.txt', 'w', encoding='utf-8') as file:
        for item in list:
            file.write(f'{item[2]} | {item[0]} {item[1]}\n')
