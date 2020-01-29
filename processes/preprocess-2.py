import sys
import time
import timeit

from VC_collections import marc, project
from VC_collections.logger import initialize_logger

sys.path.insert(
    1, "C:/Users/Yaelg/Google Drive/National_Library/Python/VC_Preprocessing"
)
from VC_collections.files import get_branch_colletionID
from VC_collections.value import *

from VC_collections.authorities import *
from VC_collections.Collection import Collection


def retrieve_collection():
    CMS, branch, collection_id = get_branch_colletionID()
    return Collection(CMS, branch, collection_id)


def is_collection_postprocess1(collection):
    try:
        return type(collection.df_final_data) == pd.DataFrame
    except:
        return False


def main():
    start_time = timeit.default_timer()
    collection = retrieve_collection()

    """ initialize logger for the logging file for that collection"""
    initialize_logger(collection.branch, collection.collection_id)
    logger = logging.getLogger(__name__)
    logger.info(
        f"\n Starting new preprocess of {collection.collection_id}, at: {datetime.now()}"
    )

    logger.info(
        f'\nStarting new preprocess {"/".join(str(sys.modules[__name__])[:-1].split("/")[-3:])} of '
        f"{collection.collection_id}, at: {datetime.now()}"
    )
    time.sleep(0.5)

    if is_collection_postprocess1(collection):
        pass
    else:
        logger.error(
            f"The {collection.collection_id} Catalog did not pass the preprocessing-1 pipe!"
            f"please run preprocess_1.py for this Catalog "
        )
        sys.exit()

    # create MARC 911 and 093 field for Call Number (סימול פרויקט)
    logger.info("[911/093] Creating 911/093 MARC field for Call Number")
    collection.df_final_data = marc.create_MARC_911(collection.df_final_data)
    collection.df_final_data.index = collection.df_final_data["911_1"].apply(
        lambda x: x[x.find("$$a") + 3 : x.find("$$c")]
    )

    # Add MMS id to catalog (מספר מערכת עלמא)
    logger.info("[001] Add MMS id to catalog")
    collection.df_final_data, df_alma = project.get_alma_sid(
        collection.aleph_custom04_path,
        collection.collection_id,
        collection.df_final_data,
    )

    # create 008
    logger.info(f"[008] Creating initial MARC 008 field")
    collection.df_final_data = marc.create_MARC_initial_008(collection.df_final_data)

    # create 351 (רמת תיאור)
    logger.info(f"[351] Creating initial MARC 351 - LEVEL OF DESCRIPTION")
    collection.df_final_data = marc.create_MARC_351_LDR(collection.df_final_data)

    # create 520 (תיאור)
    logger.info(f"[520] Creating initial MARC 520 - SCOPE AND CONTENT")
    collection.df_final_data = marc.create_MARC_520(collection.df_final_data)

    # create 245 (כותרת)
    logger.info(f"[245] Creating initial MARC 245 - UNITITLE")
    collection.df_final_data = marc.create_MARC_245(collection.df_final_data)

    # create 110 and 100 (FIRST CREATORS CORPS and PERS) (יוצר ראשון - איש/ יוצר ראשון = מוסד)
    collection.df_final_data = marc.create_MARC_100_110(collection.df_final_data)

    # create 700 and 710 (added creators PERS and CORPS) (יוצרים נוספים - אישים/יוצרים נוספים - מוסד)
    collection.df_final_data = marc.create_MARC_700_710(collection.df_final_data)

    # create 300 (EXTENT) (היקף)
    logger.info("[MARC 300] Creating ")
    collection.df_final_data = marc.create_MARC_300(collection.df_final_data)

    # create 655 (ARCHIVAL_MATERIAL) (סוג חומר)
    logger.info("[MARC 655] Creating ")
    collection.df_final_data = marc.create_marc_655(collection.df_final_data)

    # create 041 (LANGUAGE) (שפה)
    logger.info("[MARC 041] Creating ")
    collection.df_final_data = marc.create_MARC_041(collection.df_final_data)

    ####################################################
    ### CREATE  COPYRIGHT FIELDS WITH DEFAULT VALUES ###
    ### fields: 542, 540, 506
    ####################################################
    logger.info("[MARC 542, 540, 506] Creating default copyright fields")

    collection.df_final_data = marc.create_MARC_defualt_copyright(
        collection.df_final_data
    )

    # create 260 (DATE fields, and PUBLICATION_COUNTRY) (מדינת פרסום, תאריך מנורמל מוקדם, תאריך מנורמל מאוחר)
    logger.info("[MARC 260] Creating")

    collection.df_final_data = marc.create_MARC_260(
        collection.df_final_data,
        "מדינת הפרסום/הצילום",
        ["תאריך מנורמל מוקדם", "תאריך מנורמל מאוחר", "תאריך חופשי"],
    )

    collection.df_final_data = marc.create_MARC_540(collection.df_final_data)

    # add 597 (CREDIT)
    collection = marc.add_MARC_597(collection)
    logger.info("[MARC 597] Creating")

    # create 921, 933 (CATALOGUER, CATALOGING DATE)
    logger.info("[MARC 921/933] Creating")

    collection.df_final_data = marc.create_MARC_921_933(collection.df_final_data)

    # create 500 (NOTES) and other fields:
    logger.info("[MARC 500] Creating MARC 500 Notes field")
    collection.df_final_data = marc.create_MARC_500(collection.df_final_data)
    collection.df_final_data = marc.create_MARC_500s_4collection(
        collection.df_final_data
    )

    # create 999 (Default values: NOULI, NOOCLC, ARCHIVE)
    logger.info(
        "[MARC 999] initializing MARC 999 with constant values: NOULI, NOOCLC, ARCHIVE"
    )
    collection.df_final_data = marc.create_MARC_999(collection.df_final_data)

    # create BAS=VIS, in alma BAS -> 906
    logger.info("[MARC 906] Adding BAS = VIS - in Alma 906")
    collection.df_final_data = marc.create_MARC_BAS(collection.df_final_data)

    # create FMT
    collection.df_final_data = marc.create_MARC_FMT(collection.df_final_data)

    # create OWN (Default value: NNL)
    logger.info(
        "[MARC 948] initializing MARC 948 - formerly OWn with constant values: NNL"
    )
    collection.df_final_data = marc.create_MARC_948(collection.df_final_data)

    # create 773 (former LKR)
    logger.info("[MARC 773] Creating MARC 773 - the hierarchical link field")
    collection.df_final_data = marc.create_MARC_773(collection.df_final_data)

    # create 336 (#TODO add description)
    logger.info("[MARC 336] Creating MARC RDA 336 ")

    collection.df_final_data, df_explode_336 = marc.create_MARC_336(
        collection.df_final_data
    )
    df2 = pd.concat([collection.df_final_data, df_explode_336], axis=1)

    # create 337 338 (#TODO add description)
    logger.info("[MARC 337/338] Creating MARC RDA 337/338 ")
    collection.df_final_data = marc.create_MARC_337_338(collection.df_final_data)

    # create 534 (#TODO add description)
    logger.info("[MARC 534] Creating MARC 534 ")
    collection.df_final_data = marc.create_MARC_534(collection.df_final_data)

    # create MARC 590
    logger.info("[MARC 590] Creating MARC RDA 590 ")
    collection.df_final_data = marc.create_MARC_590(collection.df_final_data)

    collection.temp_preprocess_file(stage="POST")

    # TODO ADD 907 (#Rossetta link)
    collection = marc.add_MARC_907(collection)

    # create MARC Catalog
    marc.create_MARC_final_table(collection)
    collection.create_marc_seq_file()

    #

    ###############################################
    ### export final dataframe to check process ###
    ###############################################
    # collection.temp_preprocess_file(stage="POST")

    ###############################################
    ###      how much time the process ran?     ###
    ###############################################
    elapsed = timeit.default_timer() - start_time
    logger.info(f"Execution Time: {elapsed}")


if __name__ == "__main__":
    main()
