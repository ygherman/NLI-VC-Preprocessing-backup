import sys
from pathlib import Path

import gspread
from oauth2client.service_account import ServiceAccountCredentials


def get_google_drive_api_path(path):
    parent = path.parent
    for x in parent.iterdir():
        if x.is_dir() and x != path:
            yield x


def get_google_drive_credentials():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive",
    ]

    for f in get_google_drive_api_path(Path.cwd()):
        if "google_drive" in f.name:
            clientsecret_file_path = f
            break
    try:
        return ServiceAccountCredentials.from_json_keyfile_name(
            clientsecret_file_path / "client_secret.json", scope
        )
    except OSError as e:
        sys.stderr.write("problem with creds!")
        return None


def connect_to_google_drive():
    # use creds to create a client to interact with the Google Drive API
    creds = get_google_drive_credentials()
    client = gspread.authorize(creds)

    return client


def find_catalog_gspread(client, collection_id):
    files = [
        file
        for file in client.list_spreadsheet_files()
        if collection_id.lower() in file["name"].lower()
    ]
    if len(files) == 0:
        sys.stderr.write(f"no file for {collection_id} found in google drive \n")
        return client, input("if you have the ID of the file, please enter manually: ")
