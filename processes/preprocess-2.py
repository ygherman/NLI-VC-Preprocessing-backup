import sys
import time
import timeit

from VC_collections import marc, project

sys.path.insert(1, 'C:/Users/Yaelg/Google Drive/National_Library/Python/VC_Preprocessing')
from VC_collections.files import get_branch_colletionID
from VC_collections.value import *

from VC_collections.authorities import *
from VC_collections.Collection import Collection


def retrieve_colletion():
    CMS, branch, collection_id = get_branch_colletionID()
    return Collection(CMS, branch, collection_id)


def is_collection_postprocess1(collection):
    try:
        return type(collection.df_final_data) == pd.DataFrame
    except:
        return False


def main():
    start_time = timeit.default_timer()
    collection = retrieve_colletion()
    collection.logger.info(f'\nStarting new preprocess {"/".join(str(sys.modules[__name__])[:-1].split("/")[-3:])} of '
                           f'{collection.collection_id}, at: {datetime.now()}')
    time.sleep(0.5)

    if is_collection_postprocess1(collection):
        pass
    else:
        sys.stderr.write(f"The {collection.collection_id} Catalog did not pass the preprocessing-1 pipe!"
                         f"please run preprocess_1.py for this Catalog ")
        sys.exit()

    # create MARC 911 and 093 field for Call Number (סימול פרויקט)
    collection.df_final_data = marc.create_MARC_911(collection.df_final_data)
    collection.df_final_data.index = collection.df_final_data['911_1'].apply(lambda x:
                                                                             x[x.find('$$a') + 3:x.find('$$c')])

    # Add MMS id to catalog (מספר מערכת עלמא)
    collection.df_final_data, df_alma = project.get_alma_sid(collection.aleph_custom04_path, collection.collection_id,
                                                             collection.df_final_data)

    # create 008
    collection.df_final_data = marc.create_MARC_initial_008(collection.df_final_data)

    # create 520 (תיאור)
    collection.df_final_data = marc.create_MARC_351_LDR(collection.df_final_data)

    # create 351 (רמת תיאור)
    collection.df_final_data = marc.create_MARC_520(collection.df_final_data)

    # create 245 (כותרת)
    collection.df_final_data = marc.create_MARC_245(collection.df_final_data)

    # create 110 and 100 (FIRST CREATORS CORPS and PERS) (יוצר ראשון - איש/ יוצר ראשון = מוסד)
    collection.df_final_data = marc.create_MARC_100_110(collection.df_final_data)

    # create 700 and 710 (added creators PERS and CORPS) (יוצרים נוספים - אישים/יוצרים נוספים - מוסד)
    collection.df_final_data = marc.create_MARC_700_710(collection.df_final_data)

    # create 300 (EXTENT) (היקף)
    collection.df_final_data = marc.create_MARC_300(collection.df_final_data)

    # create 655 (ARCHIVAL_MATERIAL) (סוג חומר)
    collection.df_final_data = marc.create_marc_655(collection.df_final_data)

    # create 041 (LANGUAGE) (שפה)
    collection.df_final_data = marc.create_MARC_041(collection.df_final_data)

    ####################################################
    ### CREATE  COPYRIGHT FIELDS WITH DEFAULT VALUES ###
    ### fields: 542, 540, 506
    ####################################################
    collection.df_final_data = marc.create_MARC_defualt_copyright(collection.df_final_data)

    # create 260 (DATE fields, anc PUBLICATION_COUNTRY) (מדינת פרסום, תאריך מנורמל מוקדם, תאריך מנורמל מאוחר)
    collection.df_final_data = marc.create_MARC_260(collection.df_final_data, 'מדינת הפרסום/הצילום',
                                                    ['תאריך מנורמל מוקדם', 'תאריך מנורמל מאוחר'])

    # create 921, 933 (CATALOGUER, CATALOGING DATE) (שם הרושם, תאריך הרישום)


    ###############################################
    ### export final dataframe to check process ###
    ###############################################
    collection.temp_preprocess_file(stage="POST")

    ###############################################
    ###      how much time the process ran?     ###
    ###############################################
    elapsed = timeit.default_timer() - start_time
    collection.logger.info(f'Execution Time: {elapsed}')


if __name__ == '__main__':
    main()
