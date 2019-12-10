import sys
import timeit

from alphabet_detector import AlphabetDetector

from VC_collections.columns import *

sys.path.insert(1, 'C:/Users/Yaelg/Google Drive/National_Library/Python/VC_Preprocessing')
from VC_collections.project import ROOTID_finder

from VC_collections.files import get_branch_colletionID
from VC_collections.value import *

from VC_collections.authorities import *


def temp_preprocess_file(collection):
    dt_now_temp = datetime.now().strftime('%Y%m%d')
    preprocess_filename = collection.data_path_raw / (collection.collection_id + "_" + dt_now_temp +
                                                      '_preprocessing_test.xlsx')
    write_excel(collection.full_catalog, preprocess_filename, 'Catalog')


def check_missing_rootids(collection):
    root_ids = list(set(collection.full_catalog['ROOTID'].tolist()))
    missing_root_ids = list()
    collection.logger.info("[ROOTID's] checking for missing root ids in the index")
    for value in root_ids:
        if value in collection.full_catalog.index or value == "" or value == collection.collection_id:
            continue
        else:
            collection.logger.error("[ROOTID] Error - ROOTIDs that don't have corresponding unitid: " + str(value))
            missing_root_ids.append(str(value))

    assert (len(missing_root_ids) == 0), \
        "" "The following ROOT IDs do not appear in UNITID: \n {}".format(', '.join(missing_root_ids))


def create_ROOT_id(collection):
    df = collection.full_catalog
    collection.logger.info(f'Collection is of type {type(collection)}')
    collection.logger.info("Creating ROOTIDs column")
    df['ROOTID'] = df.index
    df.loc[df.index[1:], 'ROOTID'] = df.loc[df.index[1:], 'ROOTID'].apply(ROOTID_finder)

    collection.logger.info(f'Collection is of type {type(collection)}')

    # reset ROOTID of section record to null
    if len(df[df['LEVEL'] == 'Section Record']) == 1:
        df.loc[collection.collection_id, "ROOTID"] = ''

    else:
        collection.logger.error("[ROOTID] Error - There is more than one record with LEVEL='Section Record'")
        print("There is more than one record with LEVEL='Section Record'")
        sys.exit()

    collection.full_catalog = df
    return collection


def remove_unnecessary_cols(collection):
    if 'סימול אב' in list(collection.df_catalog.columns) and 'ROOTID' in list(collection.df_catalog.columns):
        collection.logger.info(f'Removing previous ROOTID column')
        collection.df_catalog = drop_col_if_exists(collection.df_catalog, 'ROOTID')

    unnamed_columns = [col for col in list(collection.df_catalog) if 'unnamed' in col]
    for col in unnamed_columns:
        collection.logger.info(f'Removing {col} column from Catalog')
        drop_col_if_exists(collection.df_catalog, col)


def clean_headers(df):
    headers = list(df.columns)
    headers = [x.upper().strip() for x in headers]
    df.columns = headers
    return df


def drop_cols_not_in_mapping(df):
    ad = AlphabetDetector()
    for header in list(df.columns):
        if ad.is_hebrew(header) and clean_text(header) not in list(field_mapper.keys()):
            df = drop_col_if_exists(df, header)

        if ad.is_latin(header) and header not in list(field_mapper.values()):
            df = drop_col_if_exists(df, header)
    return df


def remove_definition_row(collection):
    if collection.df_catalog['UNITID'].str.contains('שדה חובה').any():
        collection.logger.info(f'Removing definition row from catalog table, at {datetime.now()}')
        collection.df_catalog.drop(collection.df_catalog.index[0], inplace=True)

    if collection.df_collection['UNITID'].str.contains('שדה חובה').any():
        collection.logger.info(f'Removing definition row from collection table, at {datetime.now()}')
        collection.df_collection.drop(collection.df_collection.index[0], inplace=True)

    return collection


def map_level_to_eng(df):
    return df.replace({'LEVEL': level_mapper})


def check_mandatory_cols_v1(df):
    mandatory_cols_version1 = ['UNITID', 'LEVEL', 'UNITITLE', 'EXTENT',
                               'CATALOGUER', 'DATE_CATALOGING', 'COMBINED_CREATORS']

    #     assert (mandatory_cols in list(df.columns)), "not all mandatory columns exist in table"
    for col in mandatory_cols_version1:
        assert (col in list(df.columns)), "Mandatory element [{}] no in table".format(col)
        mask = df[col] == ''
        assert (len(df[mask]) == 0), "Mandatory element [{}] is empty in {} rows, {}".format(col,
                                                                                             len(df[mask]),
                                                                                             df.loc[
                                                                                                 df[mask].index.values,
                                                                                                 'UNITID'])


def check_mandatory_cols_v2(df):
    creators_cols = [x for x in list(df.columns) if 'CREATOR' in x]
    mandatory_cols_version2 = ['UNITID', 'LEVEL', 'UNITITLE', 'EXTENT',
                               'CATALOGUER', 'DATE_CATALOGING'] + creators_cols

    #     assert (mandatory_cols in list(df.columns)), "not all mandatory columns exist in table"
    for col in mandatory_cols_version2:
        assert (col in list(df.columns)), "Mandatory element [{}] no in table".format(col)


def check_unitid(collection):
    df = collection.full_catalog
    df = df.reset_index()

    df['UNITID'] = df['UNITID'].apply(whiteSpaceStriper)

    dup_unitid = dupCheck(df, 'UNITID')

    # assert type(dup_unitid) == str, collection.logger.info(
    #     f'[UNITID] These UNITID reoccur: ", {dup_unitid.UNITID.unique}')
    collection.logger.info(f'[UNITID] no non-unique values found')

    df = df.set_index('UNITID')
    collection.full_catalog = df

    return collection


def clean_record_title(collection):
    # replace first comma in title to hyphen
    clean_title = lambda x: x.replace(',', ' -', 1)
    collection.logger.info('[UNITITLE] Replacing first comma in title with hyphen')
    df = collection.full_catalog
    df.UNITITLE = df.UNITITLE.astype(str)
    df['UNITITLE'] = df['UNITITLE'].apply(clean_title)

    collection.full_catalog = df
    return collection


def create_personalities_report(collection):
    collection.logger.info(f'[Personalities] Creating a dataframe for creators which are persons, at: {datetime.now()}')
    df = collection.full_catalog
    try:
        'PERSNAME' in list(df.columns)

    except:
        sys.stderr("There is no [PERSNAME] column in full catalog dataframe")
        return collection

    df = remove_duplicate_in_column(df, "PERSNAME")

    df = df.reset_index()
    if "COMBINED_CREATORS_PERS" in df.columns.values:
        print("COMBINED_CREATORS_PERS in df.columns.values")
        df_creator_pers = pd.DataFrame.from_dict(
            create_authority_file(
                df[['UNITID', 'COMBINED_CREATORS_PERS']].dropna(how='any'), 'COMBINED_CREATORS_PERS'), orient='index')
    else:
        df_creator_pers = pd.DataFrame.from_dict(
            create_authority_file(
                df[['UNITID', 'CREATOR_PERS']].dropna(how='any'), 'CREATOR_PERS'), orient='index')

    # create a dataframe for personalities in the access points (persname) which are persons
    df_access_pers = pd.DataFrame.from_dict(
        create_authority_file(
            df[['UNITID', 'PERSNAME']].dropna(how='any'), 'PERSNAME'), orient='index')

    df_creator_pers = df_creator_pers.reset_index()
    df_access_pers = df_access_pers.reset_index()

    df_creator_pers['Name'] = df_creator_pers['index'].apply(
        lambda x: find_name(x).strip() if isinstance(x, str) else x)
    df_creator_pers['Role'] = df_creator_pers['index'].apply(
        lambda x: find_role(x).strip() if isinstance(x, str) else x)
    df_creator_pers['Type'] = "CREATOR"

    df_access_pers['Name'] = df_access_pers['index'].apply(lambda x: find_name(x).strip() if isinstance(x, str) else x)
    df_access_pers['Role'] = df_access_pers['index'].apply(lambda x: find_role(x).strip() if isinstance(x, str) else x)
    df_access_pers['Type'] = "PERSNAME"

    df_pers = pd.concat([df_creator_pers, df_access_pers])
    df_pers['Count'] = df_pers.apply(lambda row: len(row["UNITID"]), axis=1)

    df_pers = pd.concat(
        [df_pers['Name'], df_pers['Role'], df_pers['Type'], df_pers['Count'], df_pers['UNITID'].apply(pd.Series)],
        axis=1)

    unique_pers_filename = collection.authorities_path / (collection.collection_id + '_pers_unique_' +
                                                          collection.dt_now + '.xlsx')
    pers_occurrences_filename = collection.authorities_path / (collection.collection_id + '_pers_report_' +
                                                          collection.dt_now + '.xlsx')
    df_pers = df_pers.reset_index()
    collection.logger.info(f'[Personalities] creating report for unique personalities, file name: {unique_pers_filename}')
    write_excel(pd.DataFrame(df_pers.Name.unique()), unique_pers_filename, 'unique_pers')

    # sort by index (names of pers) and then by count (number of occurrences)
    df_pers = df_pers.reset_index(drop=True)
    df_pers = df_pers.set_index('Name')
    df_pers = df_pers.sort_values(by=['Name', 'Count'], ascending=[True, False])
    df_pers = drop_col_if_exists(df_pers, 'index')
    write_excel(df_pers, pers_occurrences_filename, 'pers_report')

    collection.full_catalog = df

    return collection


def main():
    start_time = timeit.default_timer()

    CMS, branch, collection_id = get_branch_colletionID()
    collection = Collection(CMS, branch, collection_id)
    collection.logger.info(f'\n Starting new preprocess of {collection_id}, at: {datetime.now()}')

    collection.logger.info(f'[HEADERS] Changing Hebrew column names into English - according to field_mapper, '
                           f'for {collection.collection_id}, collection record table and collection catalog'
                           f'table')

    collection.logger.info(f'[HEADERS] Cleaning headers for {collection_id} Catalog, at:   {datetime.now()}')
    collection.full_catalog = drop_cols_not_in_mapping(collection.full_catalog)

    collection = clean_tables(collection)

    if 'FIRST_CREATOR_PERS' in list(collection.full_catalog.columns):
        check_mandatory_cols_v2(collection.full_catalog.reset_index())
    else:
        check_mandatory_cols_v1(collection.full_catalog.reset_index())

    collection.logger.info(
        f'[LEVEL] Mapping Level values of {collection_id} from hebrew to english, at: {datetime.now()}')
    collection.full_catalog = map_level_to_eng(collection.full_catalog)

    collection.logger.info(f'[UNITID] checking for duplicate values, at: {datetime.now()}')
    collection = check_unitid(collection)

    assert collection.full_catalog.index.name == 'UNITID'

    collection = create_ROOT_id(collection)

    elapsed = timeit.default_timer() - start_time
    collection.logger.info(f'Execution Time: {elapsed}')

    if 'TO_DELETE' in list(collection.full_catalog.columns):
        collection.logger.info(
            "[TO_DELETE] Changing the ROOTID to collectionID for records which are about to be deleted")
        collection.full_catalog.columns.loc[collection.full_catalog.columns['TO_DELETE'] == 'כן',
                                            'ROOTID'] = collection.collection_id

    collection = clean_record_title(collection)

    collection.logger.info(
        f'[COMBINED_CREATORS] CREATING COMBINED CREATORS for {collection_id} , at: {datetime.now()}')
    collection = clean_creators(collection)

    collection.logger.info(
        f'[COMBINED_CREATORS]Splitting COMBINED_CREATORS into COMBINED_CREATORS_PERS'
        f'and COMBINED_CREATORS_CORPS columns according to roles')
    collection.full_catalog = split_creators_by_type(collection.full_catalog, 'COMBINED_CREATORS')

    collection = create_personalities_report(collection)





    temp_preprocess_file(collection)







if __name__ == '__main__':
    main()
