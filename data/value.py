"""
SYNOPSIS
    TODO helloworld [-h,--help] [-v,--verbose] [--version]

DESCRIPTION
    TODO This describes how to use this script. This docstring
    will be printed by the script if there is an error or
    if the user requests help (-h or --help).
    
PROJECT NAME:
    untitled

AUTHOR
    Yael Vardina Gherman <Yael.VardinaGherman@nli.org.il>
    Yael Vardina Gherman <gh.gherman@gmail.com>

LICENSE
    This script is in the public domain, free from copyrights or restrictions.

VERSION
    Date: 29/07/2019 15:31
    
    $
"""
from datetime import datetime

import dateutil
from fuzzywuzzy import process


def isNaN(value):
    """
    Checks whether the given value is a NaN.

    :param value: the value to check
    :return: True for NaN and false if not a NaN
    """
    return value != value


def find_nth(string, searchFor, n):
    """
    finds the n'th occurrence of a substring (searchFor) in a string.

    :param string: the string to search
    :param searchFor: the substring to search for
    :param n: the position number
    :return: The position of the nth occurence of the substring in the given string.
    """

    start = string.find(searchFor)
    while start >= 0 and n > 1:
        start = string.find(searchFor, start + len(searchFor))
        n -= 1
    return start


def check_missing_data(df):
    """
    Check Missing Data
    :param df: the dataframe to check
    :return: a sorted list of null values
    """
    # check for any missing data in the df (display in descending order)
    return df.isnull().sum().sort_values(ascending=False)


def utf8len(s):
    """
    checks the length of a given utf8 encoded s string
    :param s: the string to check
    :return: the lentgh of a the given string s
    """
    return len(s.encode('utf-8'))


# ##

# In[1]:


def create_list(x, delimiter):
    """
        create list from a string with specified delimiter
    :param x: the string to turn to list
    :param delimiter: the delimiter to split the string by
    :return: return the list that was created from the given x string
    """
    x_list = x.split(delimiter)
    x_list = [x.strip() for x in x_list]
    return x_list

def unique_list(text):
    """
        Create a unique list with give string text
    :param text: the given string
    :return: returns a unique list of objects split by semicolon
    """
    text = [x.strip() for x in text.split(";")]
    return ";".join(list(set(text)))


def date_validate(date_text):
    """
        Validate a given Date passed as string type
    :param date_text: the date string to check
    """
    try:
        datetime.strptime(date_text, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DD")

# strip trailing semicolon finction
semiColonStriper = lambda x: x.rstrip(';')


# Cleaning Text from special Charecters
clean_text = lambda x: ''.join(e for e in str(x) if e.isalnum())

# # strip whitespaces function
whiteSpaceStriper = lambda x: x.strip()


def replace_lst_dict(lst, dictionary):
    for k,v in enumerate(lst):
        if v in dictionary:
            lst[k] = dictionary[v]
    return lst


def format_cat_date(df):
    if clean_text('תאריך הרישום') in list(df.columns):
        cat_date_col = clean_text('תאריך הרישום')
    else:
        cat_date_col = process.extractOne('date_cataloguing', list(df.columns))

    df[cat_date_col] = df[cat_date_col].apply(str)

    df[cat_date_col] = df[cat_date_col].apply(lambda x:
                                              datetime.strftime(dateutil.parser.parse(x), '%Y%m')
                                              if len(x) > 6 else x)

    return df