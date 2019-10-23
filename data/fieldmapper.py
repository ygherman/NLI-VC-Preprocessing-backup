"""
SYNOPSIS
    TODO helloworld [-h,--help] [-v,--verbose] [--version]

DESCRIPTION
    TODO This describes how to use this script. This docstring
    will be printed by the script if there is an error or
    if the user requests help (-h or --help).
    
PROJECT NAME:
    helper_fuctions

AUTHOR
    Yael Vardina Gherman <Yael.VardinaGherman@nli.org.il>
    Yael Vardina Gherman <gh.gherman@gmail.com>

LICENSE
    This script is in the public domain, free from copyrights or restrictions.

VERSION
    Date: 22/08/2019 15:54
    
    $
"""


aleph_field_mapper = {
        'ברקוד': 'BARCODE',
        'סימולמקורי': 'ORIDINAL_ID',
        'סימולפרויקט': 'UNITID',
        'סימול': 'UNITID',
        'סימולמספרמזהה': 'UNITID',
        'רמתתיאור': 'LEVEL',
        'כותרת': 'UNITITLE',
        'קודתיקארכיון': 'ARCHIV_ID',
        'מספרהמיכל': 'CONTAINER',
        'מיכל': 'CONTAINER',
        'מספרמיכל': 'CONTAINER',
        'מספרהמיכלבונמצאהתיקפריט': 'CONTAINER',
        'מידענוסף': 'SCOPECONTENT',
        'תיאור': 'SCOPECONTENT',
        'תאריךחופשי': 'DATE',
        'תאריךמנורמל': 'DATE_NORMAL',
        'תאריך': 'DATE_NORMAL',
        'תאריךמנורמלמוקדם': 'DATE_START',
        'תאריךמנורמלמאוחר': 'DATE_END',
        'תאריךתצלוםחפץ/טקסטמוערמוקדם': 'PHOTO_DATE_EARLY',
        'תאריךתצלוםחפץ/טקסטמוערמאוחר': 'PHOTO_DATE_LATE',
        'פומבי': 'PUBLIC',
        'יוצרים': 'COMBINED_CREATORS',
        'יוצרראשיאיש': 'FIRST_CREATOR_PERS',
        'סוגיוצרראשיאיש': 'TYPE_FIRST_CREATOR_PERS',
        'יוצריםנוספיםאיש': 'ADD_CREATOR_PERS',
        'יוצרראשימוסד': 'FIRST_CREATOR_CORP',
        'שםיוצרראשימוסד': 'FIRST_CREATOR_CORP',
        'סוגיוצרראשימוסד': 'TYPE_FIRST_CREATOR_CORP',
        'יוצריםנוספיםמוסד': 'ADD_CREATOR_CORPS',
        'היקףהחומר': 'EXTENT',
        'היקף': 'EXTENT',
        'סוגחומר': 'ARCHIVAL_MATERIAL',
        'סוגהחומר': 'ARCHIVAL_MATERIAL',
        'מדיהפורמט': 'MEDIUM_FORMAT',
        'קנהמידה': 'SCALE',
        'טכניקה': 'TECHNIQUE',
        'מדינתהפרסוםהצילום': 'PUBLICATION_COUNTRY',
        'מדינתהפרסום': 'PUBLICATION_COUNTRY',
        'מקוםהפרסום': 'PUBLICATION_COUNTRY',
        'מילותמפתחאישים': 'PERSNAME',
        'מילותמפתחמקומות': 'GEOGNAME',
        'מילותמפתחמוסדות': 'CORPNAME',
        'מילותמפתחארגונים': 'CORPNAME',
        'מילותמפתחיצירות': 'WORKS',
        'מילותמפתחנושאים': 'SUBJECT',
        'מגבלותפרטיות': 'ACCESSRESTRICT',
        'מגבלותלתצוגהבאינטרנט': 'ACCESSRESTRICT',
        'שםהרושם': 'CATALOGUER',
        'רושם': 'CATALOGUER',
        'שםהמקטלג': 'CATALOGUER',
        'תאריךהרישום': 'DATE_CATALOGING',
        'תאריךרישום': 'DATE_CATALOGING',
        'תאריךקיטלוג': 'DATE_CATALOGING',
        'מסלולדיגיטציה': 'DIGITIZATION',
        'דיגיטציה': 'DIGITIZATION',
        'נשלחלדיגיטציה': 'DIGITIZATION',
        'סריקהדוצדדית': 'TWO_SIDE_SCAN',
        'סריקתדוצדדית': 'TWO_SIDE_SCAN',
        'מספרקבציםמוערך': 'EST_FILE_NUM',
        'מספרקבציםמוערך': 'EST_FILES_NUM',
        'מספרקבציםלסריקה': 'EST_FILE_NUM',
        'הערותגלוילמשתמשקצה': 'NOTES',
        'הערותלאגלוילמשתמש': 'NOTES_HIDDEN',
        'תאריךפתיחתרשומה': 'RECORD_CREATE_DATE',
        'מידעעלסידורהחומר': 'ARRANGEMENT',
        'מידעעלסידורהאוסףשיטתהסידור': 'ARRANGEMENT',
        'מידעעלהצטברותהחומר': 'BIOGHIST',
        'מידעעלהצטברותהאוסף': 'BIOGHIST',
        'תיאורהחומרבפרויקטתרבותחזותיתואמנויותהבמה': 'APPRAISAL',
        'אוסףפתוח': 'ACCURALS',
        'מיקוםפיזי': 'PHYSLOC',
        'הערות': 'NOTES',
        'מידות': 'SIZE',
        'למחיקה': 'TO_DELETE',
        'סימולאב': 'ROOTID',
        'מידות': 'DIMENSIONS',
    }

field_mapper_back = {
        'ACCESSRESTRICT': 'מגבלות פרטיות',
        'ACCURALS': 'אוסף פתוח',
        'ADD_CREATORS': 'יוצרים נוספים',
        'ADD_CREATORS_CORPS': 'שמות ארגונים יוצרים נוספים',
        'ADD_CREATORS_PERS': 'שמות אישים יוצרים נוספים',
        'APPRAISAL': 'תיאור החומר בפרויקט תרבות חזותית ואמנויות הבמה',
        'ARCHIVAL_FILE_NUMBER': 'קוד תיק ארכיון',
        'ARCHIVAL_MATERIAL': 'סוג החומר',
        'ARRANGEMENT': 'מידע על סידור החומר',
        'BARCODE': 'ברקוד',
        'BIOGHIST': 'מידע על הצטברות החומר',
        'BOX': 'מספר מיכל',
        'CONTAINER': 'מספר מיכל',
        'CATALOGUER': 'שם הרושם',
        'CATALOGUING_DATE': 'שם הרישום',
        'COMBINED_CREATORS': 'יוצרים',
        'COMBINED_CREATORS_CORPS': 'יוצרים - מוסדות',
        'COMBINED_CREATORS_PERS': 'יוצרים - אישים',
        'CONTAINER': 'מספר מיכל',
        'CORPNAME': 'מילות מפתח_מוסדות',
        'CORPSNAME': 'מילות מפתח_מוסדות',
        'CREATOR_CORPS': 'יוצרים - מוסדות',
        'CREATOR_PERS': 'יוצרים - אישים',
        'DATE': 'תאריך חופשי',
        'DATE_END': 'תאריך מנורמל מאוחר',
        'DATE_NORMAL': 'תאריך',
        'DATE_START': 'תאריך מנורמל מוקדם',
        'DIGITIZATION': 'נשלח לדיגיטציה',
        'DIMENSIONS': 'מידות',
        'EARLY_NORMAL_DATE': 'תאריך מנורמל מוקדם',
        'EST_FILE_NUM': 'מספר קבצים מוערך',
        'EST_FILES_NUM': 'מספר קבצים מוערך',
        'ESTFILESNUM': 'מספר קבצים מוערך',
        'EXTENT': 'היקף החומר',
        'GEOGNAME': 'מילות מפתח_מקומות',
        'PUBLICATION_COUNTRY': 'מדינת הפרסום/הצילום',
        'LATE_NORMAL_DATE': 'תאריך קטלוג מאוחר',
        'LEAVES': 'רמה תחתונה',
        'LEVEL': 'רמת תיאור',
        'MEDIUM_FORMAT': 'מדיה + פורמט',
        'NOTES': 'הערות',
        'ORIDINAL_ID': 'סימול מקורי',
        'Parent': 'סימול אב',
        'PERSNAME': 'מילות מפתח_אישים',
        'PHYSLOC': 'מיקום פיזי',
        'PROJECT_ID': 'סימול פרויקט',
        'ROOTID': 'סימול אב',
        'SCALE': 'קנה מידה',
        'SCOPECONTENT': 'תיאור',
        'STAGE': 'שלב ביצירה',
        'SUBJECT': 'מילות מפתח_נושאים',
        'TECHNIQUE': 'טכניקה',
        'TWO_SIDE_SCAN': 'סריקה דו-צדדית',
        'TWOSIDESCAN': 'סריקה דו-צדדית',
        'UNITID': 'סימול פרויקט',
        'UNITITLE': 'כותרת',
        'WORKNAME': 'מילות מפתח_יצירות',
        'WORKNAME2': 'מילות מפתח - יצירות 2',
        'WORKS': 'מילות מפתח_יצירות',
        'SIZE': 'מידות',
        'DATE_CATALOGING': 'תאריך הרישום',
        'TO_DELETE': 'למחיקה',
        'BIBLIOGRAPHY': 'ביבליוגרפיה ומקורות מידע',
        'NOTES_HIDDEN': 'הערות לא גלוי למשתמש',
        'ARCHIV_ID': 'קוד תיק ארכיון',
        'RELATED_MATERIAL': 'חומרים קשורים',
        'COLLECTION_TYPE': 'סוג אוסף'
    }

level_mapper = {
    'אוסף':'Section Record',
    'חטיבה':'Fonds Record',
    'תתחטיבה':'Sub-Fonds Record',
    'סדרה':'Series Record',
    'תתסדרה':'Sub-Series Record',
    'תת סדרה':'Sub-Series Record',
    'תיק':'File Record',
    'פריט':'Item Record',
    'סידרה':'Series Record',
    'תתסידרה':'Sub-Series Record'
}

collection_field_mapper = {
    'סימול האוסף': 'UNITID',
    'סימול מקורי': 'ORIDINAL_ID',
    'רמת תיאור': 'LEVEL',
    'שם האוסף': 'UNITITLE',
    'תאריך חופשי': 'DATE',
    'יוצרי האוסף': 'COMBINED_CREATORS',
    'מילות מפתח_אישי ליבה': 'PERSNAME',
    'מילות מפתח_מוסדות ליבה': 'CORPSNAME',
    'מילות מפתח_יצירות ליבה': 'WORKS',
    'מילות מפתח_נושאי ליבה': 'SUBJECT',
    'סוג חומר': 'ARCHIVAL_MATERIAL',
    'היסטוריה ארכיונית': 'BIOGHIST',
    'תיאור הטיפול באוסף בפרויקט': 'APPRAISAL',
    'סוג אוסף': 'COLLECTION_TYPE',
    'היקף': 'EXTENT',
    'אוסף פתוח': 'ACCURALS',
    'ביבליוגרפיה ומקורות מידע': 'BIBLIOGRAPHY',
    'מיקום פיזי': 'PHYSLOC',
    'חומרים קשורים': 'RELATED_MATERIAL',
    'הערות - גלוי למשתמש קצה': 'NOTES',
    'הערות - לא גלוי למשתמש קצה': 'NOTES_HIDDEN',
    'שם הרושם': 'CATALOGUER',
    'תאריך הרישום': 'DATE_CATALOGING'
}

class FieldMapper:

    def __init__(self):
        self.aleph_field_mapper = aleph_field_mapper
        self.field_mapper_back = field_mapper_back
        self.level_mapper = level_mapper
        self.collection_field_mapper = collection_field_mapper
