from datetime import datetime
from pony.orm import *

db = Database()


class Record(db.Entity):
    collection = Required("Collection")
    mms_id = PrimaryKey(str, auto=True)
    unitid = Required(str, unique=True, index="unitid")
    rootid = Required(str)
    barcode = Optional(str)
    original_id = Optional(str)
    level = Required(str)
    container = Optional(str)
    archiv_id = Optional(str)
    unititle = Required(str)
    unititle_eng = Optional(str)
    scopecontent = Optional(str)
    date = Optional(str)
    date_start = Required(datetime)
    date_end = Required(datetime)
    photo_date_early = Optional(str)
    photo_date_late = Optional(str)
    combined_creators = Required(str)
    combined_creators_pers = Optional(str)
    combined_creators_corps = Optional(str)
    persname = Optional(str)
    corpname = Optional(str)
    works = Optional(str)
    subject = Optional(str)
    archival_material = Optional(str)
    medium_format = Optional(str)
    scale = Optional(str)
    technique = Optional(str)
    publication_country = Optional(str)
    geogname = Optional(str)
    accessrestrict = Optional(str)
    digitization = Optional(str)
    two_side_scan = Optional(str)
    est_files_num = Optional(int)
    true_files_num = Optional(int)
    language = Optional(str)
    extent = Optional(str)
    duration = Optional(str)
    notes = Optional(str)
    notes_hidden = Optional(str)
    cataloguer = Required(str)
    date_cataloging = Optional(datetime)
    bioghist = Optional(str)
    appraisal = Optional(str)
    collection_type = Optional(str)
    accurals = Optional(str)
    bibliography = Optional(str)
    physloc = Optional(str)
    related_materials = Optional(str)


class Collection(db.Entity):
    collection_id = PrimaryKey(str)
    name_heb = Optional(str)
    name_eng = Optional(str)
    branch = Required("Branch")
    current_owner = Optional(str)
    records = Set(Record)
    credit_heb = Optional(str)
    credit_eng = Optional(str)


class Branch(db.Entity):
    id = PrimaryKey(int, auto=True)
    name_heb = Optional(str)
    name_eng = Optional(str)
    collections = Set(Collection)


def main():
    @db.on_connect(provider="sqlite")
    def sqlite_case_sensitivity(db, connection):
        cursor = connection.cursor()
        cursor.execute("PRAGMA case_sensitive_like = OFF")

    db.bind(
        provider="sqlite",
        filename=r"\\172.0.12.30\Visual_Art\DB\NLI_VC_DB.db",
        create_db=True,
    )

    db.generate_mapping(create_tables=True)


if __name__ == "__main__":
    main()
