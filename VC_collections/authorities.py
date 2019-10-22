import os
import pandas as pd
from .AuthorityFiles import *
from .files import write_excel


def split_creators_by_type(df, col_name):
    """
    take the col name of the col that contains multiple creators (corps+pers) and split them in to\
    2 different columns take the add_creators column and split it in to add_pers and add_corp according to the role.
    if the role is in the corps role, and if the role in in the pers role list

    :param df: The original Dataframe
    :param col_name:  the column name which contains the creators
    :return:
    """
    #
    #
    #
    #
    for index, row in df.iterrows():
        add_pers_creators = []
        add_corps_creators = []
        for creator in str(row[col_name]).split(';'):
            for k, v in Authority_instance.roles_dict.items():
                if find_role(creator) in v:
                    if "pers" in k:
                        add_pers_creators.append(creator)
                    else:
                        add_corps_creators.append(creator)
        if "CREATOR_" in df.columns.values:
            if str(row['CREATOR_PERS']) != "":
                add_pers_creators.append(
                    str(row['CREATOR_PERS']).strip() + ' [' + str(row['CREATOR_PERS_ROLE']).strip() + ']')
            if str(row['CREATOR_CORP']) != "":
                add_corps_creators.append(
                    str(row['CREATOR_CORP']).strip() + ' [' + str(row['CREATOR_CORP_ROLE']).strip() + ']')

        add_pers_creators = list(filter(None, add_pers_creators))
        add_corps_creators = list(filter(None, add_corps_creators))

        df.loc[index, "COMBINED_CREATORS_PERS"] = ";".join(add_pers_creators)
        df.loc[index, "COMBINED_CREATORS_CORPS"] = ";".join(add_corps_creators)
    if 'COMBINED_CREATORS' in df.columns.values:
        df.COMBINED_CREATORS = df.COMBINED_CREATORS.str.strip()
    df.COMBINED_CREATORS_CORPS = df.COMBINED_CREATORS_CORPS.str.strip()
    df.COMBINED_CREATORS_PERS = df.COMBINED_CREATORS_PERS.str.strip()
    return df


def create_authority_file(df, col_name, delimiter=';'):
    """
    creates an authority file of values in a given column (col_name)
    of a given DataFrame.
    The values in the cells of the column are delimited with a
    semicolon ;

    :param delimiter:
    :param df: the dataframe to work on
    :param col_name:
    :return: returns a dictionary of all named authorities in the column
    """

    # create an empty dictionary of authorities
    authority_list = {}

    for item, frame in df[col_name].iteritems():
        if not pd.isnull(frame):
            if ";" in str(frame):
                names = frame.split(delimiter)
                for name in names:
                    authority_list = create_authority(
                        df, item, name.strip(), authority_list)
            else:
                authority_list = create_authority(
                    df, item, str(frame).strip(), authority_list)

    return authority_list


def create_authority(df, index, frame, authority_list):
    """
    Creates a dictionary of all the authorities in a Dataframe

    :param authority_list: the entire authority dictionary of the DataFrame
    :param frame: the value of the cell
    :param index: index of the frame
    :rtype: dict
    :type df: pd.DataFrame
    :param df:
    """

    if frame not in authority_list:
        authority_list[frame] = {}
        authority_list[frame]['UNITID'] = []
    if "[" in frame:
        authority_list[frame]['role'] = find_role(frame)
    else:
        authority_list[frame]['role'] = ''

    authority_list[frame]['UNITID'].append(df.loc[index, 'UNITID'])

    return authority_list


def authority_Excelfile(df, column):
    """
    creates an authority datafames of a given column
    :param df:
    :param column:
    :return: the authority dataframe
    """
    df = df.reset_index()
    df_auth = pd.DataFrame.from_dict(create_authority_file(df[['UNITID', column]].dropna(how='any'),
                                                           column),
                                     orient='index')
    # create new column to count the number of occurrences
    df_auth['COUNT'] = df_auth['UNITID'].apply(lambda x: len(x))

    # split list of unitids into columns
    df_auth = pd.concat([df_auth['COUNT'],
                         df_auth['UNITID'].apply(pd.Series)], axis=1)
    return df_auth


def create_match_file(branch, collectionID, df_authority_file, df_auth, column):
    """

    :param branch:
    :param collectionID:
    :param df_authority_file:
    :param df_auth:
    :param column:
    """
    file_name = collectionID + '_' + column + '.xlsx'
    choices = list()
    match_results = dict()

    choices = choices + df_authority_file.index.tolist()

    if column == "ARCHIVAL_MATERIAL":
        for index, frame in df_authority_file.iterrows():
            choices.append(frame["ARCHIVAL_MATERIAL"])
            if str(frame['ARCHIVAL_MATERIAL_ALT_HEB']) == '':
                continue
            else:
                choices += frame['ARCHIVAL_MATERIAL_ALT_HEB']

    if column == "MEDIUM_FORMAT":
        choices = df_authority_file['MEDIA_FORMAT'].tolist()

    # fuzzy matching process
    for value in df_auth.index:
        from fuzzywuzzy import process
        match_results[value] = process.extract(value, choices, limit=4)

    new_match_results = dict()
    for key, value in match_results.items():
        choich, score = value[0]
        if str(score) != '100':
            new_match_results[key] = value

    # create a dataframe from the match results

    df_match_results = pd.DataFrame.from_dict(new_match_results)
    df_match_results = df_match_results.transpose()
    # df_match_results['Match'] = np.where('100' not in df['אפשרות1'], 'No', 'Yes')
    # df_match_results['Match'] =
    #                          ['No'if '100' in x  else 'Yes' for x in df_match_results[df_match_results.columns[0]]]
    if len(new_match_results) > 0:
        df_match_results.columns = ['אפשרות1', 'אפשרות2', 'אפשרותו3', 'אפשרות4']

    # split the tuple of the value and match score into 2 columns
    #     for cols in df_match_results.columns.values:
    #         df_match_results[['match'+cols, 'score'+cols]] = df[cols].apply(pd.Series)

    # create a list of sheet names
    sheets = list()
    sheets.append(collectionID + '_' + column + '_c')
    sheets.append(collectionID + '_' + column)
    sheets.append(column + '_match_results')

    combined_results = pd.concat([df_match_results, df_auth], axis=1)

    # create a list of dataframe that should
    dfs = list()
    dfs.append(combined_results)
    dfs.append(df_auth)
    dfs.append(df_match_results)

    write_excel(dfs, os.path.join(os.getcwd(), branch, collectionID, 'Authorities', file_name), sheets)


def is_corp(creator, df_corp_roles):
    """
        Checks if Creator is a Corporation (including role in brackets)
    :param creator: the creator to check
    :param df_corp_roles: the dataframe of the roles to check against
    :return: True if the creator is a Corporation, False if otherwise
    """
    if find_role(creator) in df_corp_roles.loc[:, 'CREATOR_CROPS_ROLE'].tolist():
        return True
    else:
        return False


def is_pers(creator, df_pers_roles):
    """
        Checks if Creator is a Person  (including role in brackets)
    :param creator: the creator to check
    :param df_pers_roles: the dataframe of the roles to check against
    :return: True if the creator is a Person, False if otherwise
    """
    if find_role(creator) in df_pers_roles.loc[:, 'CREATOR_PERS_ROLE'].tolist():
        return True
    else:
        return False


def find_role(name):
    """
    from a given name string value returns only the name.
    Ex. אפרתי משה [צלם]  returns only צלם

    :rtype: str
    :type name: str
    :return: returns the role of the creator
    :param name: the value of the a creator with a role
    """
    if '[' in name:
        start = name.find('[') + 1
        return name[start:-1]
    else:
        return ""


def find_name(name):
    """"
    from a given name string value returns only the name.
    Ex. אפרתי משה [צלם]  returns only אפרתי משה

    :rtype: str
    :param name: the value of the a creator with a role
    :return: only the name of the given string
    """
    if "[" in name:
        start = name.find('[')
        return name[:start].rstrip()
    else:
        return name.rstrip()


# #

# In[23]:


def map_role_to_relator(role, df, lang, mode='PERS'):
    """
        Map role to RDA Relator
    :param role: the original role to map
    :param df: the original
    :param lang: the language of the role
    :param mode: personalities or corporations
    :return: the dataframe with the mapped relator values
    """
    if mode == "PERS":
        if lang == 'heb':
            return df.loc[df[df["CREATOR_PERS_ROLE"] == role].index.item(), 'RELATOR_HEB']
        if lang == 'eng':
            return df.loc[df[df["CREATOR_PERS_ROLE"] == role].index.item(), 'RELATOR_ENG']
    elif mode == "CORPS":
        if lang == 'heb':
            return df.loc[df[df["CREATOR_CROPS_ROLE"] == role].index.item(), 'RELATOR_HEB']
        if lang == 'eng':
            return df.loc[df[df["CREATOR_CROPS_ROLE"] == role].index.item(), 'RELATOR_ENG']
