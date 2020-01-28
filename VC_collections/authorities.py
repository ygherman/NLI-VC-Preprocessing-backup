import difflib
import logging
import os
import pprint
import re
from collections import defaultdict

import pandas as pd
from fuzzywuzzy import process

from VC_collections import Collection
from VC_collections.AuthorityFiles import *
from VC_collections.columns import clean_text_cols, strip_whitespace_af_semicolon, remove_duplicate_in_column, \
    drop_col_if_exists, replace_NaN
from VC_collections.files import write_excel
from VC_collections.value import clean_name

logger = logging.getLogger(__name__)


def split_creators_by_type(df, col_name):
    """
    take the col name of the col that contains multiple creators (corps+pers) and split them in to\
    2 different columns take the add_creators column and split it in to add_pers and add_corp according to the role.
    if the role is in the corps role, and if the role in in the pers role list

    :param df: The original Dataframe
    :param col_name:  the column name which contains the creators
    :return: df: the modified dataframe with two new columns - creators_pers and creators corps
    """

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
    else:
        df.COMBINED_CREATORS = df['FIRST_CREATOR_PERS'].astype(str) + ';' + df['FIRST_CREATOR_CORP'] + ';' + \
                               df["COMBINED_CREATORS_PERS"] + ';' + df["COMBINED_CREATORS_CORPS"]

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
    df = df.reset_index(drop=True)
    df_auth = pd.DataFrame.from_dict(create_authority_file(df[['UNITID', column]].dropna(how='any'),
                                                           column),
                                     orient='index')
    # create new column to count the number of occurrences
    df_auth['COUNT'] = df_auth['UNITID'].apply(lambda x: len(x))

    # split list of unitids into columns
    df_auth = pd.concat([df_auth['COUNT'],
                         df_auth['UNITID'].apply(pd.Series)], axis=1)
    return df_auth


def create_match_file(collection, df_authority_file, df_auth, column):
    """

    :param collection:
    :param df_authority_file:
    :param df_auth:
    :param column:
    """
    file_name = collection.collection_id + '_' + column + '.xlsx'
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
        choice, score = value[0]
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
    sheets.append(collection.collection_id + '_' + column + '_c')
    sheets.append(collection.collection_id + '_' + column)
    sheets.append(column + '_match_results')

    combined_results = pd.concat([df_match_results, df_auth], axis=1, sort=True)

    # create a list of dataframe that should
    dfs = list()
    dfs.append(combined_results)
    dfs.append(df_auth)
    dfs.append(df_match_results)

    write_excel(dfs, collection.authorities_path / file_name, sheets)


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
    name = name.strip()
    if '[' in name:
        start = name.find('[') + 1
        return name[start:name.find(']')]
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
        return clean_name(name[:start].rstrip())
    else:
        return clean_name(name.rstrip())


def create_combined_creators(row):
    if row['FIRST_CREATOR_PERS'] != '':
        first_creator = str(row['FIRST_CREATOR_PERS']) + ' [' + str(row['TYPE_FIRST_CREATOR_PERS']) + ']'
    else:
        first_creator = str(row['FIRST_CREATOR_CORP']) + ' [' + str(row['TYPE_FIRST_CREATOR_CORP']) + ']'

    if 'ADD_CREATORS' in list(row.index):
        add_creators = row['ADD_CREATORS']
    else:
        add_creators = str(row['ADD_CREATOR_PERS']) + ';' + str(row['ADD_CREATOR_CORPS'])

    combined_creators = f'{first_creator};{add_creators}'

    combined_creators.rstrip(';')
    combined_creators.lstrip(';')
    combined_creators.replace(';;', ';')

    return combined_creators


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


def unique_creators(df):
    """
        Check that the value in COMBINED_CREATORS do not appear in the CONTROL_ACCESS columns: PERNAME, CORPNAME.
        Create a new combined creators column which contains only values that do not appear in PERNAME and
        CORPNAME columns/
    :param df:
    :return:
    """
    characters_to_filter = [None, np.nan, ' ']
    for index, frame in df.iterrows():
        l1 = str(frame['COMBINED_CREATORS']).split(";")
        creator_names = set([find_name(x) for x in l1])

        new_persnames = str(frame['PERSNAME']).split(';')
        new_persnames = list(filter(None, new_persnames))
        if len(new_persnames) > 0:
            new_persnames = [x for x in new_persnames if x not in creator_names]

        new_corpsnames = list(filter(None, str(frame['CORPNAME']).split(';')))
        if len(new_corpsnames) > 0:
            new_corpsnames = [x for x in new_corpsnames if x not in creator_names]

        df.loc[index, 'PERSNAME'] = ';'.join(new_persnames)
        df.loc[index, 'CORPNAME'] = ';'.join(new_corpsnames)

    return df


def clean_empty_indexes(indexes_roles_not_found):
    new_indexes_roles_not_found = []
    for key, value in indexes_roles_not_found:
        if key == '':
            continue
        new_indexes_roles_not_found.append((key, value))
    return new_indexes_roles_not_found


def map_relators(df, authority_role_list):
    """

    :param authority_role_list:
    :param collection:
    :return:
    """
    df["COMBINED_CREATORS"] = df["COMBINED_CREATORS"].str.strip('\n')
    df["COMBINED_CREATORS"] = df["COMBINED_CREATORS"].str.rstrip('')

    # initiate empty lists
    temp_role_dict = defaultdict(list)
    roles = []
    role_not_found = []

    indexes_roles_not_found = []
    for index, row in df.iterrows():
        for creator in str(row['COMBINED_CREATORS']).strip().split(';'):
            temp_role = find_role(creator)
            roles.append(temp_role)
            if temp_role.strip() not in authority_role_list:
                indexes_roles_not_found.append((temp_role, index))

    for role_1, index_1 in indexes_roles_not_found:
        temp_role_dict[role_1].append(index_1)

    # Check which role does not appear in the authority file of creators role (persons and corporates)
    for role in roles:
        if role.strip() in authority_role_list:
            continue
        else:
            role_not_found.append(role)

    role_not_found = list(set(x for x in role_not_found if x != 'nan' or x != ''))
    indexes_roles_not_found = clean_empty_indexes(indexes_roles_not_found)

    if len(indexes_roles_not_found) != 0:
        logger.error(f"[CREATORS] Roles check - list of roles not found in roles authority list:"
                                f" {'; '.join(role_not_found)}.")
    return roles, role_not_found, temp_role_dict


def correct_relators(collection: Collection, authority_role_list: list,
                     roles: list,  role_not_found: list,
                     temp_role_dict: dict):
    """

    :param collection:
    :param authority_role_list:
    :param roles:
    :param role_not_found:
    :param temp_role_dict:
    """

    def create_error_report():
        """

        """
        res = [(role,) + item for role in role_not_found for item in
               process.extract(role, authority_role_list, limit=5)]
        df_roles = pd.DataFrame(res, columns=['role', 'match', 'match score'])
        df_indexes_roles_not_found = pd.DataFrame.from_dict(temp_role_dict, orient='index').transpose()
        df_roles_sheets = ['roles not found', 'example_items']

        dfs_roles_list = [df_roles, df_indexes_roles_not_found]

        roles_check_file_name = collection.collection_id + '_roles_check' + collection.dt_now + '.xlsx'
        collection.logger.info(f"[ROLES] Creating {collection.collection_id} _roles_check_ "
                               f"{collection.dt_now}.xlsx file")

        write_excel(dfs_roles_list, os.path.join(collection.authorities_path, roles_check_file_name), df_roles_sheets)

    role_not_found = list(filter(None, role_not_found))

    if len(role_not_found) > 0:
        for role in role_not_found:
            collection.logger.info("[ROLES] Printing roles that are not found - and the options for corrections")
            pprint.pprint(str(role))
            pprint.pprint(process.extract(str(role), authority_role_list))
        pprint.pprint(set(role_not_found))
        create_error_report()

    else:
        logger.info("[ROLES] all values matched to creator roles controlled vocabulary")


def clean_creators(collection: Collection) -> Collection:
    """

    :param collection:
    :return:
    """
    df = collection.full_catalog
    df = replace_NaN(df)

    authority_role_list = list(set(Authority_instance.df_creator_corps_role['CREATOR_CROPS_ROLE'])) + \
                          list(set(Authority_instance.df_creator_pers_role['CREATOR_PERS_ROLE']))

    creators_cols = [col for col in df.columns if "CREATOR" in col]
    if 'COMBINED_CREATORS' in creators_cols:
        creators_cols.remove('COMBINED_CREATORS')
        collection.logger.info("[CREATORS] COMBINED_CREATORS found: 1 creators column")
        for col in creators_cols:
            df = drop_col_if_exists(df, col)
        df = remove_duplicate_in_column(df, 'COMBINED_CREATORS')
    elif 'FIRST_CREATOR_PERS' in creators_cols:
        df['COMBINED_CREATORS'] = df[creators_cols].apply(create_combined_creators, axis=1)

    assert 'COMBINED_CREATORS' in list(df.columns), print(list(df.columns))

    roles, role_not_found, temp_role_dict = map_relators(df, authority_role_list)
    df = clean_text_cols(df, 'COMBINED_CREATORS')
    df = strip_whitespace_af_semicolon(df, 'COMBINED_CREATORS')

    df = unique_creators(df)
    correct_relators(collection, authority_role_list, roles, role_not_found, temp_role_dict)

    df['COMBINED_CREATORS'] = df['COMBINED_CREATORS'].str.replace(";;", ";")


    collection.full_catalog = df

    return collection



def check_values_against_cvoc(collection: Collection, col: str, mapping_dict: dict) -> list:
    """

    :param collection:
    :param df:
    :param col:
    :param mapping_dict:
    :return:
    """
    pass


def convert_dict(new_val2errs):
    d = defaultdict(list)
    for nv, errs in new_val2errs.items():
        if type(errs) == str:
            errs = errs.split(';')
        for err in errs:
            if err != '':
                d[err].append(nv)
    return d


def find_new_value(err, error_words2possible_new_vals):
    try:
        close_match4err = difflib.get_close_matches(err, list(error_words2possible_new_vals.keys()), n=1, cutoff=0.6)[0]
    except IndexError:
        return None

    possible_new_vals = error_words2possible_new_vals[close_match4err]
    if len(possible_new_vals) == 1 or possible_new_vals[0] == possible_new_vals[1]:
        return possible_new_vals[0]

    print('\n'.join([f"{i} :{pnv}" for pnv, i in enumerate(possible_new_vals)]))
    while True:
        try:
            new_val_i = int(input(f"insert the index of the matching new value for error word {err}.\n "
                                  f"if no new val is right return -1\n"))
            break
        except ValueError:
            print("You did not enter an index in the desired range, please try again.")

    return None if new_val_i == -1 else possible_new_vals[new_val_i]


def fix_values_in_column(col, err, new_val):
    if new_val is not None:
        if new_val != err:

            col = col.apply(lambda x: x.split(';'))
            try:

                fixed_col = col.apply(lambda line: [re.sub(r'^' + err + r'$', new_val, val.strip()) for val in line])
            except:
                print(f"Bad error value: [{err}], please correct in original data, and run again.")

            col = fixed_col.apply(lambda x: ';'.join(x))
        return None, col
    return err, col


def fix_original(col, error_words, new_values):
    error_words2possible_new_val = convert_dict(new_values)
    missing_errs = []
    for err in error_words:
        if len(err) > 0:
            ret, col = fix_values_in_column(col, err, find_new_value(err, error_words2possible_new_val))
            if ret is not None:
                missing_errs.append(ret)
    return missing_errs, col


def check_values_against_cvoc(df, col_name, new_values):
    logger = logging.getLogger(__name__)
    test_list = [x.split(';') for x in df[col_name].tolist()]
    vals_to_check = [item for sublist in test_list for item in sublist]
    vals_to_check = list(set(vals_to_check))

    values_not_found, df[col_name] = fix_original(df[col_name], vals_to_check, new_values)
    if len(values_not_found) > 0:
        print("These values were not found: ", values_not_found)
    else:
        logger.info(f'[{col_name.upper()}] Values corrected in column {col_name}')

    return df
