from sqlalchemy import create_engine, exists
import pandas as pd
import sys
import logging, os, time
from VC_collections.columns import drop_col_if_exists

sys.path.insert(
    1, r"C:\Users\Yaelg\Google Drive\National_Library\Python\VC_Preprocessing"
)
from VC_collections import AuthorityFiles

branches = {
    "אדריכלות": "1",
    "אדריכלות - מבחר מייצג": "5",
    "מחול": "2",
    "מחול - מבחר מייצג": "6",
    "עיצוב": "3",
    "עיצוב - מבחר מייצג": "7",
    "תיאטרון": "4",
    "תיאטרון - מבחר מייצג": "8",
}


collection_table_field_mapper = {
    "אשכול": "branch",
    "סימול האוסף": "collection_id",
    "שם הארכיון": "name_heb",
    "שם הארכיון באנגלית": "name_eng",
    "בעלים נוכחי": "current_owner",
    "קרדיט עברית": "credit_heb",
    "קרדיט אנגלית": "credit_eng",
}


def check_vpn():

    PING_HOST = "172.0.12.30"  # some host on the other side of the VPN

    response = os.system(f"ping {PING_HOST}")

    if response == 0:
        pingstatus = "Network Active"
    else:
        pingstatus = "Network Error"
        logging.warning("Network Error")
        sys.exit()

    return pingstatus


def replace_branch_with_fk(df):
    df["branch"] = df["branch"].map(branches)
    return df


def main():
    pingstatus = check_vpn()
    engine = create_engine("sqlite:///X:\\db\\NLI_VC_DB.db", echo=True)
    df = AuthorityFiles.Authority_instance.df_credits.rename(
        columns=collection_table_field_mapper
    )
    cols = [
        col for col in list(df.columns) if col in collection_table_field_mapper.values()
    ]
    df_final = df[cols]
    df_final.index.name = "collection_id"

    df_final = replace_branch_with_fk(df_final)

    print(df_final.columns)

    df_final.to_sql("Collection", con=engine, if_exists="replace")


if __name__ == "__main__":
    main()
