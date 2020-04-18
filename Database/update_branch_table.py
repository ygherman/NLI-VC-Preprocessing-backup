from sqlalchemy import create_engine, exists
import pandas as pd
import sys
import logging, os, time
from VC_collections.columns import drop_col_if_exists
from tabulate import tabulate


sys.path.insert(
    1, r"C:\Users\Yaelg\Google Drive\National_Library\Python\VC_Preprocessing"
)
from VC_collections import AuthorityFiles


branches = {
    "1": {"name_heb": "אדריכלות", "name_eng": "Architecture"},
    "5": {
        "name_heb": "אדריכלות - מבחר מייצג",
        "name_eng": "Architecture - representative selection",
    },
    "2": {"name_heb": "מחול", "name_eng": "Dance"},
    "6": {
        "name_heb": "מחול - מבחר מייצג",
        "name_eng": "Dance - representative selection",
    },
    "3": {"name_heb": "עיצוב", "name_eng": "Design"},
    "7": {
        "name_heb": "עיצוב - מבחר מייצג",
        "name_eng": "Design - representative selection",
    },
    "4": {"name_heb": "תיאטרון", "name_eng": "Theater"},
    "8": {
        "name_heb": "תיאטרון - מבחר מייצג",
        "name_eng": "Theater - representative selection",
    },
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


def main():
    pdtabulate = lambda df: tabulate(df, headers="keys", tablefmt="psql")

    pingstatus = check_vpn()
    engine = create_engine("sqlite:///X:\\db\\NLI_VC_DB.db", echo=True)
    df = pd.DataFrame(branches, columns=branches.keys())
    df = df.transpose()

    df.index.name = "id"

    print(pdtabulate(df))

    df.to_sql("Branch", con=engine, if_exists="replace")


if __name__ == "__main__":
    main()
