import sys, glob, os
from pathlib import Path
from sqlalchemy import create_engine
import logging

sys.path.insert(
    1, r"C:\Users\Yaelg\Google Drive\National_Library\Python\VC_Preprocessing"
)
from VC_collections import Collection

column_mapping = {
    "סימול": "unitid",
    "סימול אב": "rootid",
    "ברקוד": "barcode",
    "סימול מקורי": "original_id",
    "רמת תיאור": "level",
    "מספר מיכל": "container",
    "קוד תיק ארכיון": "archiv_id",
    "כותרת": "unititle",
    "כותרת אנגלית": "unititle_eng",
    "תיאור": "scopecontent",
    "תאריך חופשי": "date",
    "תאריך מנורמל מוקדם": "date_start",
    "תאריך מנורמל מאוחר": "date_end",
    "תאריך יצירת החפץ / הטקסט המקורי מוקדם": "photo_date_early",
    "תאריך יצירת החפץ / הטקסט המקורי מאוחר": "photo_date_late",
    "יוצרים": "combined_creators",
    "יוצרים אישים": "combined_creators_pers",
    "יוצרים מוסדות": "combined_creators_corps",
    "מילות מפתח - אישים": "persname",
    "מילות מפתח - מוסדות": "corpname",
    "מילות מפתח_יצירות": "works",
    "מילות מפתח_נושאים": "subject",
    "סוג חומר": "archival_material",
    "מדיה + פורמט": "medium_format",
    "קנה מידה": "scale",
    "טכניקה": "technique",
    "מדינת הפרסום/הצילום": "publication_country",
    "מילות מפתח_מקומות": "geogname",
    "מגבלות פרטיות": "accessrestrict",
    "מסלול דיגיטציה": "digitization",
    "סריקה דו-צדדית": "two_side_scan",
    "מספר קבצים מוערך": "est_files_num",
    "מספר קבצים לאחר דיגיטציה": "actual_files_num",

    "שפה": "language",
    "היקף החומר": "extent",
    "משך": "duration",
    "הערות גלוי למשתמש קצה": "notes",
    "הערות לא גלוי למשתמש": "notes_hidden",
    "שם הרושם": "cataloguer",
    "תאריך הרישום": "date_cataloging",
    "בעלים נוכחי": "current_owner",
    "היסטוריה ארכיונית": "bioghist",
    "תיאור הטיפול באוסף בפרויקט": "appraisal",
    "סוג אוסף": "collection_type",
    "אוסף פתוח": "accurals",
    "ביבליוגרפיה ומקורות מידע": "bibliography",
    "מיקום פיזי": "physloc",
    "חומרים קשורים": "related_materials",
}
branches = ['Architect', 'Dance', 'Design', 'Theater']


def get_all_collections(branches:dict, base_path) -> dict:
    logging.info("getting all collections in all branches")
    collections = dict()
    for br in branches:
        collections[br] = list()

    for branch in branches:
        for file in glob.glob(os.path.join(base_path, 'VC-' + branch) + '/*'):
            if '.' in os.path.basename(file):
                continue
            collections[branch].append(os.path.basename(file))
    return collections



def prepare_table_to_insert(df, collection_id):
    logging.info(f"Preparing {collection_id} to be inserted into DB")

    df = df.rename(columns=column_mapping)
    df.index.name = "mms_id"
    df["collection"] = collection_id
    return df


def main():
    base_path = r'C:\Users\Yaelg\Google Drive\National_Library\Python'
    collections = get_all_collections(branches, base_path)

    for branch in branches:
        for collection_id in collections[branch]:
            collection = Collection.Collection(CMS="alma", branch=branch, collection_id=collection_id)

            # collection = Collection.retrieve_collection()
            df = prepare_table_to_insert(collection.df_final_data, collection.collection_id)
            engine = create_engine(r"sqlite:///\\172.0.12.30\Visual_Art\Master_Catalog\NLI_VC_DB.db", echo=True)
            df.to_sql("Record", con=engine, if_exists="append")
            logging.info(f"commited {branch}/{collection_id}  into DB")


if __name__ == "__main__":
    main()

    # while True:
    #     main()
    #     batch = input("Enter another catalog to DB? (Y/N) ")
    #     if batch.strip().lower() != "y":
    #         sys.stdout.write("Ending run!")
    #         sys.exit()
    # main()
