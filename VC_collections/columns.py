
import collections
import pprint

import numpy as np
import pandas as pd


def column_exists(df, col):
    """
    checks whether a column exists in a given dataframe
    :param df: the dataframe
    :param col: the column name to check
    :return:
    """
    return col in list(df.columns)


def remove_duplicate_in_column(df, col):
    """
    check for duplicate values for each row in a Column 'col' of a dataframe 'df'
    :param df: the dataframe to check
    :param col: the column in which to search form duplicate values
    :return: the duplicate free dataframe
    """

    for index, frame in df[col].iteritems():

        # if there is a list of values delimited by ;
        if ';' in str(frame):
            old_values_list = frame.split(';')
            # check if there are duplicate values
            #             print('len old:', len(old_values_list), 'len new:',len(set(old_values_list)))
            if len(old_values_list) > len(set(old_values_list)):

                print("There are duplicates in column {}, index {}".format(col, index))
                pprint.pprint([item for item, count in collections.Counter(old_values_list).items() if count > 1])
                new_values_list = ";".join(list(set(old_values_list)))

            else:
                new_values_list = ";".join(old_values_list)

        # if there is only 1 value
        else:
            new_values_list = frame

        # update the column with the new list of unique values per cell
        df.loc[index, col] = new_values_list

    return df


def dupCheck(df, column_name):
    """
    Checks for duplicate values in a Dataframe df, in a specific column_name.
    :param df:
    :param column_name:
    :return: A dataframe of all duplicated/non-unique values of the string "no non-unique values found"
    """
    try:
        return pd.concat(g for _, g in df.groupby(column_name) if len(g) > 1)
    except:
        return "no non-unique values found"


def is_column_empty(df, col):
    """
    Checks that column is not empty
    :param df: the dataframe
    :param col: the column name to check if empty
    :return: true if the column is empty, false if otherwise
    """
    s_temp = df[col].replace('', np.nan)
    return s_temp.isnull().all()


def clean_text_cols(df, col):
    """remove leading white space in coloumn.
    remove trailing white space in coloumn.
    remove double space in coloumn.

    :param df: the dataframe

    :param col: the column to clean

    :return: the clean dataframe
    """
    df[col] = df[col].apply(str)
    # remove leading white space
    df[col] = df[col].str.lstrip()
    # remove trailing white space
    df[col] = df[col].str.rstrip()
    df[col] = df[col].str.strip()

    # remove double space
    df[col] = df[col].apply(lambda x: " ".join(x.split()))

    # remove space comma space
    df[col] = df[col].str.replace(" , ", ", ")

    df[col] = df[col].str.rstrip(";")
    df[col] = df[col].str.rstrip(",")

    df[col] = df[col].str.lstrip(";")
    df[col] = df[col].str.rstrip(",")

    df[col] = df[col].str.replace("''", '"')
    df[col] = df[col].str.lstrip(',')
    df[col] = df[col].str.lstrip(':')

    # remove leading white space
    df[col] = df[col].str.lstrip()

    df[col] = df[col].str.strip('\n')

    return df


def drop_col_if_exists(df, col):
    """
    Drop Column if exists
    :param df: the original dataframe
    :param col: the column to drop from dataframe
    :return: the new dataframe
    """
    if col in list(df.columns.values):
        return df.drop(col, axis=1)
    else:
        return df


def rstrip_semicolon(df, col):
    """
    strip semicolumn from end of string in a column

    col -
    :param df: the dataframe to work on
    :param col: the name of the column to work on
    :return: the clean dataframe
    """
    df[col] = df[col].apply(str)
    df[col] = df[col].str.rstrip(';')
    return df


def strip_whitespace_af_semicolon(df, col):
    """
    strip whitespace after semicolon

    :param df: df - the dataframe to work on
    :param col: col - the name of the column to work on
    :return: the clean dataframe
    """
    df[col] = df[col].apply(str)
    from data.value import semiColonStriper
    df[col] = df[col].apply(semiColonStriper)
    return df


def create_marc_008(df):
    """
        for next version of the master table positions 15-17 in 008, need to be populated according to the
        [מדינת פרסום] field and be mapped to the list of country codes of the LoC

    :param df: the original df
    :return:
    """
    return df

