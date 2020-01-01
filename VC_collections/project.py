"""
SYNOPSIS
    TODO helloworld [-h,--help] [-v,--verbose] [--version]

DESCRIPTION
    TODO This describes how to use this script. This docstring
    will be printed by the script if there is an error or
    if the user requests help (-h or --help).
    
PROJECT NAME:
    helper_fuctions

AUTHOR
    Yael Vardina Gherman <Yael.VardinaGherman@nli.org.il>
    Yael Vardina Gherman <gh.gherman@gmail.com>

LICENSE
    This script is in the public domain, free from copyrights or restrictions.

VERSION
    Date: 30/07/2019 13:04
    
    $
"""
import os
import sys

import pandas as pd

from VC_collections.columns import drop_col_if_exists
from VC_collections.value import clean_text, find_nth

# ROOTID finder
ROOTID_finder = lambda x: x[:find_nth(x, '-', x.count('-'))] if '-' in x else ''


def get_aleph_sid(custom04_path, collectionID, df):
    """
        Get Aleph sys ID

    :param custom04_path: the path to the file with the aleph system ID's
    :param collectionID: the collection ID
    :param df: the dataframe to add the aleph system number to
    :return: the Dataframe with a system number column
    :return:
    """
    aleph_sysno_file = os.path.join(custom04_path, collectionID + '_aleph_sysno.xlsx')
    assert os.path.isfile(aleph_sysno_file), "There is no such File: aleph_sysno_file"

    # parse sysno file
    xl2 = pd.ExcelFile(aleph_sysno_file)
    df_aleph = xl2.parse('Sheet1')

    # rename columns
    df_aleph = df_aleph.rename(columns={'Adlib reference (911a)': '911##a'})

    df_aleph = df_aleph.set_index(list(df_aleph)[1])
    df_aleph.index.names = ['סימול']
    df_aleph = df_aleph.iloc[:, 0:1]
    df_aleph.columns = ['System number']

    df = df.join(df_aleph, how='left')

    return df, df_aleph


def get_alma_sid(custom04_path, collectionID, df):
    """
        Get Aleph sys ID

    :param custom04_path: the path to the file with the aleph system ID's
    :param collectionID: the collection ID
    :param df: the dataframe to add the aleph system number to
    :return: the Dataframe with a system number column
    :return:
    """
    alma_sysno_file = os.path.join(custom04_path, collectionID + '_alma_sysno.xlsx')
    assert os.path.isfile(alma_sysno_file), "There is no such File: alma_sysno_file"

    # parse sysno file
    xl2 = pd.ExcelFile(alma_sysno_file)
    df_alma = xl2.parse(0)

    df_alma = df_alma.set_index(list(df_alma.columns)[1])
    df_alma.index.names = ['סימול']
    df_alma = df_alma.iloc[:, 0:1]

    # rename columns
    df_alma.columns = ['MMS ID']

    # convert MMS ID col to string

    df = df.merge(df_alma, on='סימול', how='left')
    print(df[df['MMS ID'].isna()])
    df = drop_col_if_exists(df, '911_1')
    try:
        df['MMS ID'] = df['MMS ID'].astype(str)
    except ValueError:
        sys.stderr.write(f"There is a missing MMS ID at {df.loc[df['MMS ID'].isna()==True, 'סימול']}."
                         f"\n Please update the Alma MMS ID for that call number and run again!")
        sys.exit()

    df = df.reset_index()
    df = drop_col_if_exists(df, '911_1')
    df = df.set_index('MMS ID')
    df.index.name = '001'
    df = drop_col_if_exists(df, '911_1')

    return df, df_alma


def get_branch_colletionID(branch='', collectionID='', batch=False):
    """
        Get Branch and CollectionID
    :param branch: the branch (Architect, Dance, Design or Theater
    :param collectionID: The collection ID
    :param batch: if the calling results from a batch process
    :return: The branch and the collection ID
    """
    if not batch:
        while True:
            CMS = input("Preprecessing for Aleph - write 'Aleph'; Preprocessing for Alma - write 'Alma")
            CMS = CMS.lower()

            branch = input("Please enter the name of the Branch (Architect, Design, Dance, Theater): ")
            branch = str(branch)
            if branch[0].islower():
                branch = branch.capitalize()
            if branch not in ['Dance', 'Architect', 'Theater', 'Design']:
                print('need to choose one of: Architect, Design, Dance, Theater')
                continue
            else:
                # we're happy with the value given.
                branch = 'VC-' + branch
                break

        while True:
            collectionID = input("please enter the Collection ID:")
            if not collectionID:
                print("Please enter a collectionID.")
            else:
                # we're happy with the value given.
                break
    elif batch:
        return 'VC-' + branch, collectionID

    return CMS, branch, collectionID


def get_root_title(df, index):
    """
        Get the title of the parent record
    :param df: The original dataframe,
    :param df: The original dataframe,
    :param index:
    :return:
    """

    # print("index sent to get root title function:", index, "Level:", df.loc[index, '351'])
    if df.loc[index, '351'] == '$$cSection Record':
        return ''
    else:
        clean_column_names = [clean_text(x) for x in list(df.columns)]
        if 'סימולאב' in clean_column_names:
            parent_id = 'סימולאב'
            root_id = df.loc[index, parent_id]
        elif 'parent' in clean_column_names:
            parent_id = 'parent'
            root_id = df.loc[index, parent_id]
        else:
            root_id = ROOTID_finder(index)
        if 'כותרת' in list(df.columns):
            title = df.loc[root_id, 'כותרת']
        else:
            title = df.loc[root_id, '24510'].strip('$$a')

    return title.strip()


def get_collection_paths(collectionID):
    """
        for a given collection, return all paths of the directory structure
    :param collectionID:
    """

    return ""



