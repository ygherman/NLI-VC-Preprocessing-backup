import sys
from datetime import datetime

sys.path.insert(1, 'C:/Users/Yaelg/Google Drive/National_Library/Python/VC_Preprocessing')
from VC_collections.Collection import Collection
from VC_collections.columns import drop_col_if_exists

import timeit

from VC_collections.files import get_branch_colletionID


def clean_table(collection):
    collection.df_catalog = collection.df_catalog.rename(columns={'סימול/מספר מזהה': 'סימול'})
    collection.df_catalog = collection.df_catalog.fillna('')
    if collection.df_catalog.iloc[0].str.contains('שדה חובה!!').any() or collection.df_catalog.iloc[0].str.contains(
            'שדה חובה').any():
        collection.df_catalog = collection.df_catalog[1:]


def remove_unnecessary_cols(collection):
    if 'סימול אב' in list(collection.df_catalog.columns) and 'ROOTID' in list(collection.df_catalog.columns):
        collection.logger.info(f'Removing previous ROOTID column')
        collection.df_catalog = drop_col_if_exists(collection.df_catalog, 'ROOTID')

    unnamed_columns = [col for col in list(collection.df_catalog) if 'unnamed' in col]
    for col in unnamed_columns:
        collection.logger.info(f'Removing {col} column from Catalog')
        drop_col_if_exists(collection.df_catalog, col)


def main():
    start_time = timeit.default_timer()

    CMS, branch, collection_id = get_branch_colletionID()
    collection = Collection(CMS, branch, collection_id)
    collection.logger.info(f'Starting preprocess of {collection_id}, at: {datetime.now()}')

    print(collection.df_catalog)

    elapsed = timeit.default_timer() - start_time

    collection.logger.info(f'Execution Time: {elapsed}')


if __name__ == '__main__':
    main()
