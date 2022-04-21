import numpy as np
import pandas as pd
import unicodedata
import unidecode
import re
from itertools import permutations



def SplitNameAndEmail(row:str) -> tuple:
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

def txtToList(txtPath:str, logging=False) -> None:
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

    userList = []
    flagErrorIndex = 0
    userIsDuplicate = False

    for line in lines:
        name, email = SplitNameAndEmail(line)

        flags = ''
        if name == '' or email == '':
            continue

        # filter name
        filteredNameList = []
        for word in name:
            temp = word.translate(str.maketrans('', '', ')(!\'\":@#$.,')).upper()
            temp = remove_nonspacing_marks(temp)
            filteredNameList.append(temp)

        # filter email
        filteredEmail = email.translate(str.maketrans('', '', ')(\'\"'))
        filteredName  = ' '.join(filteredNameList)
        
        # check if the user name or user email already exists in the list
        for user in userList:
            if filteredEmail == user[0] and filteredName == user[1]:
                userIsDuplicate = True

            if filteredEmail == user[0]:
                flags = flags.join(f'-N{flagErrorIndex}')
                user[2] = user[2].join(f'-N{flagErrorIndex}')
                flagErrorIndex += 1
            if filteredName == user[1]:
                flags = flags.join(f'-E{flagErrorIndex}')
                user[2] = user[2].join(f'-E{flagErrorIndex}')
                flagErrorIndex += 1

        if not userIsDuplicate:
            userList.append([filteredEmail, filteredName, flags])
        userIsDuplicate = False

    for user in userList:
        user[2] = user[2].removeprefix('-')

    return userList

def listToTxt(list:list):
    with open('cleanFile.txt', 'w', encoding='utf-8') as file:
        for item in list:
            file.write(f'{item[2]} | {item[0]} {item[1]}\n')
