import sys
from pathlib import Path
from sqlalchemy import create_engine

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
    "שפה": "language",
    "היקף החומר": "extent",
    "משך": "duration",
    "הערות גלוי למשתמש קצה": "notes",
    "הערות לא גלוי למשתמש": "notes_hidden",
    "שם הרושם": "cataloguer",
    "תאריך הרישום": "date_cataloging",
    "היסטוריה ארכיונית": "bioghist",
    "תיאור הטיפול באוסף בפרויקט": "appraisal",
    "סוג אוסף": "collection_type",
    "אוסף פתוח": "accurals",
    "ביבליוגרפיה ומקורות מידע": "bibliography",
    "מיקום פיזי": "physloc",
    "חומרים קשורים": "related_materials",
}


def prepare_table_to_insert(df, collection_id):
    df = df.rename(columns=column_mapping).set_index("mms_id")
    df["collection"] = collection_id
    return df


def main():
    collection = Collection.retrieve_collection()
    prepare_table_to_insert(collection.df_final_data, collection.collection_id)


if __name__ == "__main__":
    main()
