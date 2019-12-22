import sys
import timeit

from alphabet_detector import AlphabetDetector

from VC_collections.columns import *

sys.path.insert(1, 'C:/Users/Yaelg/Google Drive/National_Library/Python/VC_Preprocessing')
from VC_collections.project import ROOTID_finder

from VC_collections.files import get_branch_colletionID
from VC_collections.value import *

from VC_collections.authorities import *
from VC_collections.Collection import Collection


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

    elif len(df[df['LEVEL'] == 'Section Record']) > 1:
        collection.logger.error("[ROOTID] Error - There is more than one record with LEVEL='Section Record'")
        print(df[df['LEVEL'] == 'Section Record'])
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
        assert (col in list(df.columns)), f"Mandatory element [{col}] no in table".format(col)
        mask = df[col] == ''
        assert (len(df[mask]) == 0), f"Mandatory element [{col}] is empty in {len(df[mask])} rows, " \
                                     f"{df.loc[df[mask].index.values, 'UNITID']}"


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


def create_authorities_report(collection, authority_type):

    df = collection.full_catalog

    if authority_type == "PERS":
        col = 'PERSNAME'
        combined_authority_col = "COMBINED_CREATORS_" + authority_type
        authority_col = "CREATOR_" + authority_type
    elif authority_type == "CORPS":
        col = 'CORPNAME'
        combined_authority_col = "COMBINED_CREATORS_" + authority_type
        authority_col = "CREATOR_" + authority_type
    elif authority_type == "GEO":
        col = 'GEOGNAME'
        combined_authority_col = "GEOGNAME"
        authority_col = "GEOGNAME"

    if col not in list(df.columns):
        return collection

    collection.logger.info(f'[{col}] Creating a dataframe for creators which are {authority_type}')

    try:
        col in list(df.columns)

    except:
        sys.stderr(f"There is no [{col}] column in full catalog dataframe")
        return collection

    df = remove_duplicate_in_column(df, col)

    df = df.reset_index()

    if combined_authority_col in df.columns.values:
        df_creator = pd.DataFrame.from_dict(
            create_authority_file(
                df[['UNITID', combined_authority_col]].dropna(how='any'), combined_authority_col), orient='index')
    else:
        df_creator = pd.DataFrame.from_dict(
            create_authority_file(
                df[['UNITID', authority_col]].dropna(how='any'), authority_col), orient='index')

    # create a dataframe for personalities in the access points (persname) which are persons
    df_access = pd.DataFrame.from_dict(
        create_authority_file(
            df[['UNITID', col]].dropna(how='any'), col), orient='index')

    df_creator = df_creator.reset_index()
    df_access = df_access.reset_index()

    df_creator['Name'] = df_creator['index'].apply(
        lambda x: find_name(x).strip() if isinstance(x, str) else x)
    df_creator['Role'] = df_creator['index'].apply(
        lambda x: find_role(x).strip() if isinstance(x, str) else x)
    df_creator['Type'] = "CREATOR"

    df_access['Name'] = df_access['index'].apply(lambda x: find_name(x).strip() if isinstance(x, str) else x)
    df_access['Role'] = df_access['index'].apply(lambda x: find_role(x).strip() if isinstance(x, str) else x)
    df_access['Type'] = col

    df_authority = pd.concat([df_creator, df_access])
    df_authority['Count'] = df_authority.apply(lambda row: len(row["UNITID"]), axis=1)

    df_authority = pd.concat(
        [df_authority['Name'], df_authority['Role'], df_authority['Type'],
         df_authority['Count'], df_authority['UNITID'].apply(pd.Series)],
        axis=1)

    if authority_type=='GEO':
        df_authority = df_authority[df_authority['Type'] != 'CREATOR']

    unique_authority_filename = collection.authorities_path / (collection.collection_id + '_' +
                                                               authority_type.lower() + '_unique_' +
                                                               collection.dt_now + '.xlsx')
    authority_occurrences_filename = collection.authorities_path / (collection.collection_id + '_' +
                                                                    authority_type.lower() + '_report_' +
                                                                    collection.dt_now + '.xlsx')
    df_authority = df_authority.reset_index(drop=True)
    collection.logger.info(
        f'[Authorities - {authority_type}] creating report for unique {authority_col},'
        f' file name: {unique_authority_filename}')
    write_excel(pd.DataFrame(df_authority.Name.unique()), unique_authority_filename, 'unique_' + authority_type.lower())

    # sort by index (names of pers) and then by count (number of occurrences)
    df_authority = df_authority.reset_index(drop=True)
    df_authority = df_authority.set_index('Name')
    df_authority = df_authority.sort_values(by=['Name', 'Count'], ascending=[True, False])
    df_authority = drop_col_if_exists(df_authority, 'index')
    write_excel(df_authority, authority_occurrences_filename, authority_type + '_report')

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
    elif 'COMBINED_CREATORS' in list(collection.full_catalog.columns):
        check_mandatory_cols_v1(collection.full_catalog.reset_index())
    elif 'ADD_CREATORS' in list(collection.full_catalog.columns):
        collection.full_catalog = split_creators_by_type(collection.full_catalog, 'ADD_CREATORS')

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
        f'[COMBINED_CREATORS] Splitting COMBINED_CREATORS into COMBINED_CREATORS_PERS'
        f'and COMBINED_CREATORS_CORPS columns according to roles')
    collection.full_catalog = split_creators_by_type(collection.full_catalog, 'COMBINED_CREATORS')

    collection = create_authorities_report(collection, 'PERS')
    collection = create_authorities_report(collection, 'CORPS')
    collection = create_authorities_report(collection, 'GEO')

    collection = check_values_against_cvoc(collection, 'ARCHIVAL_MATERIAL', Authority_instance.arch_mat_search_dict)
    collection = check_values_against_cvoc(collection, 'MEDIUM_FORMAT', Authority_instance.media_format_mapping_dict)

    temp_preprocess_file(collection)







if __name__ == '__main__':
    main()
