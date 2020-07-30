from unittest import TestCase, main
from unittest.mock import Mock


class TestCollection(TestCase):


    def test_add_current_owner(self):
        from VC_collections.Collection import add_current_owner
        from tests.test_data import (
            df_credits_data_with_owner_test,
            df_credits_data_without_owner_test,
            df_collection_test1,
            df_collection_test2,
        )

        df_collection_test1 = add_current_owner(
            df_collection_test1, df_credits_data_without_owner_test, "ArBe"
        )
        self.assert_(
            df_collection_test1.loc[
                df_collection_test1["רמת תיאור"] == "אוסף", "בעלים נוכחי"
            ][0],
            "",
        )
        df_collection_test2 = add_current_owner(
            df_collection_test2, df_credits_data_with_owner_test, "PDoGa"
        )
        self.assert_(
            df_collection_test1.loc[
                df_collection_test1["רמת תיאור"] == "אוסף", "בעלים נוכחי"
            ][0],
            "",
        )

    def test_map_field_names_to_english(self):
        from VC_collections.Collection import map_field_names_to_english
        import VC_collections.fieldmapper as FM
        test_column_names = {
            'סימול',
            'סימול אב',
            'ברקוד',
            'סימול מקורי',
            'רמת תיאור',
            'מספר מיכל',
            'קוד תיק ארכיון',
            'כותרת',
            'כותרת אנגלית',
            'תיאור',
            'תאריך חופשי',
            'תאריך מנורמל מוקדם',
            'תאריך מנורמל מאוחר',
            'תאריך יצירת החפץ / הטקסט המקורי מוקדם',
            'תאריך יצירת החפץ / הטקסט המקורי מאוחר',
            'יוצרים',
            'יוצרים אישים',
            'יוצרים מוסדות',
            'מילות מפתח - אישים',
            'מילות מפתח - מוסדות',
            'מילות מפתח_יצירות',
            'מילות מפתח_נושאים',
            'סוג חומר',
            'מדיה + פורמט',
            'קנה מידה',
            'טכניקה',
            'מדינת הפרסום/הצילום',
            'מילות מפתח_מקומות',
            'מגבלות פרטיות',
            'מסלול דיגיטציה',
            'סריקה דו-צדדית',
            'מספר קבצים מוערך',
            'מספר קבצים לאחר דיגיטציה',
            'שפה',
            'היקף החומר',
            'משך',
            'הערות גלוי למשתמש קצה',
            'הערות לא גלוי למשתמש',
            'שם הרושם',
            'תאריך הרישום',
            'היסטוריה ארכיונית',
            'בעלים נוכחי',
            'תיאור הטיפול באוסף בפרויקט',
            'סוג אוסף',
            'אוסף פתוח',
            'ביבליוגרפיה ומקורות מידע',
            'מיקום פיזי',
            'חומרים קשורים',
            "IE לייצוא"
        }
        self.assertTrue("NO MAPPING" in map_field_names_to_english(test_column_names, FM.catalog_field_mapper))


if __name__ == "__main__":
    main()
