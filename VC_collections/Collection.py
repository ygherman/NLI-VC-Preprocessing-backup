import logging
import os
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path
from shutil import copyfile

import gspread
import numpy as np
import pandas as pd
from alphabet_detector import AlphabetDetector
from oauth2client.service_account import ServiceAccountCredentials
from pymarc import XMLWriter, Record, Field

from VC_collections.fieldmapper import field_mapper
from VC_collections.files import create_directory, write_excel
from .files import get_google_drive_api_path


def initialize_logging(reports_path, collection_id):
    logging.basicConfig(level=logging.INFO,
                        filename=reports_path / (collection_id + '.log'),
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%y-%m-%d %H:%M',
                        )
    fh = logging.FileHandler(filename=reports_path / (collection_id + '.log'))
    logger = logging.getLogger(__name__)
    logger.addHandler(fh)

    return logger


def connect_to_google_drive():
    # use creds to create a client to interact with the Google Drive API

    scope = ['https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file",
             "https://www.googleapis.com/auth/drive"]

    for f in get_google_drive_api_path(Path.cwd()):
        if "google_drive" in f.name:
            clientsecret_file_path = f
            break

    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(clientsecret_file_path / 'client_secret.json', scope)
    except OSError as e:
        sys.stderr.write("problem with creds!")
    client = gspread.authorize(creds)

    return client


def find_catalog_gspread(client, collection_id):
    files = [file for file in client.list_spreadsheet_files() if collection_id.lower() in file['name'].lower()]
    if len(files) == 0:
        sys.stderr.write(f'no file for {collection_id} found in google drive')
        return ''

    for index, file in enumerate(files):
        print(index, ':', file['name'])
        file_index = input('which file of the following do you choose? type the index number ')
        return client, files[int(file_index)]['id']


def create_xl_from_gspread(client, file_id):
    spreadsheet = client.open_by_key(file_id)
    all_sheets_as_dfs = {}
    worksheet_list = spreadsheet.worksheets()
    for sheet in worksheet_list:
        print(sheet)
        if sheet.row_values(2) is None:
            continue
        dict_ds = sheet.get_all_records(head=1)
        df = pd.DataFrame(dict_ds)
        all_sheets_as_dfs[sheet.title] = df

    return all_sheets_as_dfs


def save_gspread_catalog(raw_data_path, dfs, collection_id):
    write_excel(list(dfs.values()), raw_data_path / (collection_id + "_PRE_FINAL.xlsx"), list(dfs.keys()))


class Collection:
    _project_branches = ['Architect', 'Dance', 'Design', 'Theater']
    _catalog_sheets = {'df_catalog': 'קטלוג',
                       'df_collection': 'אוסף',
                       'df_personalities': 'אישים',
                       'df_corporation': 'מוסדות'}

    @classmethod
    def branches(cls):
        return cls._project_branches

    @staticmethod
    def get_sheet(xl, sheet):
        """

        :param xl:
        :param sheet:
        :return:
        """
        assert (sheet in xl.sheet_names), f'sheet {sheet} does not exist in file.'
        return xl.parse(sheet)

    def make_catalog_copy(self):
        """

        :return:
        """
        print('self.data_path_raw:', self.data_path_raw)
        for file in os.listdir(self.data_path_raw):
            print('here')
            filename = os.fsdecode(file)
            print('filename:', filename)
            ext = Path(file).suffix

            if 'PRE_FINAL' in filename:  # this tests for substrings
                file_path = os.path.join(self.data_path_raw, filename)
                print('NEW COPY', filename)
                new_file = file_path.replace('.xlsx', '_save_copy.xlsx')
                try:
                    copyfile(file_path, new_file)
                except shutil.SameFileError:
                    pass
                return new_file

    @staticmethod
    def replace_table_column_names(df):
        new_columns = []

        # strip column names from special characters and whitespaces.
        for col in df.columns.values:
            col = ''.join(e for e in str(col) if e.isalnum())
            new_columns.append(col)

        new_columns1 = [col.strip().lower() for col in new_columns]

        df.columns = new_columns1

        # replace the field name according to the generic field mapper
        df = df.rename(columns=field_mapper)
        df.columns = [x.upper() for x in list(df.columns)]

        return df

    @staticmethod
    def make_one_table(self):

        # turn headers to English
        self.df_catalog = self.replace_table_column_names(self.df_catalog)
        self.df_collection = self.replace_table_column_names(self.df_collection)

        combined_catalog = None

        if self.collection_id not in self.df_catalog['UNITID'].tolist():
            # turn index to string
            self.df_collection.index = self.df_collection.index.map(str)

            combined_catalog = pd.concat([self.df_collection, self.df_catalog], axis=0, sort=True)

        assert combined_catalog is not None, 'the Collection and Catalog dataframes could not be combined'

        combined_catalog = combined_catalog.set_index('UNITID')
        combined_catalog.index = combined_catalog.index.map(str)
        return combined_catalog

    @classmethod
    def catalog_sheets(cls):
        return cls._catalog_sheets

    def fetch_data(self) -> dict:
        """
        :rtype: object

        """
        catalog_dfs = {}

        def remove_empty_rows(df):
            df = df.replace('', np.nan)
            df = df.dropna(how='all')
            if 'סימול פרויקט' in list(df.columns):
                df = df.dropna(subset=['סימול פרויקט'])

            if df.index.name is not None:
                print(df.index.name)
                index = df.index.name
                df_a = df.reset_index()
                df = df_a.reset_index().dropna().set_index(index)
            return df

        def remove_instructions_row(df):
            if df.iloc[0].str.contains('שדה חובה!!').any() or df.iloc[0].str.contains('שדה חובה').any():
                # remove instruction line
                return df.loc[1:, ]
            else:
                return df

        def get_works_sheet(xl_file, branch):
            """

            :param xl_file:
            :param branch:
            :return:
            """
            works_sheets = [x for x in xl_file.sheet_names if 'יצירות' in x]
            if 'יצירות' in works_sheets:
                return 'יצירות'
            if 'Dance' in branch:
                assert ('יצירות - מחול' in xl_file.sheet_names), ' sheet יצירות - מחול does not exist in file.'
                return 'יצירות - מחול'
            elif 'Architect' in branch:
                assert ('יצירות - אדריכלות' in xl_file.sheet_names or 'יצירות' in xl_file.sheet_names), \
                    ' sheet יצירות - אדריכלות does not exist in file.'
                return 'יצירות - מחול'
            elif 'Theater' in branch:
                assert ('יצירות - תאטרון' in xl_file.sheet_names), ' sheet יצירות - תאטרון does not exist in file.'
                return 'יצירות - תאטרון'

            else:
                return ''

        copy = self.make_catalog_copy()
        print(copy)
        try:
            xl = pd.ExcelFile(copy)
        except ValueError:
            sys.stderr.write("Invalid file path! check if collection exists.")
            exit()

        for table, sheet in Collection.catalog_sheets().items():
            original_sheet = self.get_sheet(xl, sheet)
            catalog_dfs[sheet] = remove_empty_rows(remove_instructions_row(original_sheet))
        # add WORKS sheet to dfs if there is one
        try:
            catalog_dfs['יצירות'] = remove_empty_rows(xl.parse(get_works_sheet(xl, self.branch)))
        except:
            pass
        return catalog_dfs

    def __init__(self, CMS, branch, collection_id):
        """
             Initializer / Instance Attributes
        :param CMS: To which CMS the collection is intended to be imported to
        :param branch: The name of the project branch the collection belongs to (Architect , Design, Dance, Theater)
        :param collection_id: The collection identifier (call number)
        """

        self.CMS = CMS
        self.branch = branch
        self.collection_id = collection_id
        self.dt_now = datetime.now().strftime('%Y%m%d')

        # create directory and sub-folders for collection
        self.BASE_PATH = Path('C:/Users/Yaelg/Google Drive/National_Library/Python') / ('VC-' + branch) / collection_id

        # initialize directory with all folder and sub-folders for the collection
        self.data_path, self.data_path_raw, self.data_path_processed, \
        self.data_path_reports, self.copyright_path, self.digitization_path, \
        self.authorities_path, self.aleph_custom21_path, self.aleph_manage18_path, \
        self.aleph_custom04_path = create_directory(CMS, self.BASE_PATH)

        print(self.data_path, '\n', self.data_path_raw, '\n', self.data_path_processed, '\n',
              self.data_path_reports, '\n', self.copyright_path, '\n', self.digitization_path, '\n',
              self.authorities_path, '\n', self.aleph_custom21_path, '\n', self.aleph_manage18_path, '\n',
              self.aleph_custom04_path)

        # set up logger for collection instance
        self.logger = initialize_logging(self.data_path_reports, collection_id)

        client, file_id =  find_catalog_gspread(connect_to_google_drive(), self.collection_id)
        dfs = create_xl_from_gspread(client, file_id)
        save_gspread_catalog(self.data_path_raw, dfs, self.collection_id)

        catalog_dfs = self.fetch_data()

        self.all_tables = catalog_dfs
        self.df_catalog = self.all_tables['קטלוג']
        self.df_collection = self.all_tables['אוסף']
        self.df_personalities = self.all_tables['אישים']
        self.df_corporation = self.all_tables['מוסדות']
        self.full_catalog = self.make_one_table(self)

    @property
    def create_MARC_XML(self):
        """
        Creates a MARC XML format file from the given dataframe
        :return:
        """
        df = self.full_catalog
        output_file = self.data_path_processed / (self.collection_id + '_final_' + self.dt_now + ".xml")
        writer = XMLWriter(open(output_file, 'wb'))
        start_time = time.time()
        counter = 1

        for index, row in df.iterrows():

            record = Record()

            if df.index.dtype == 'float64':
                ident = "00{}".format(str(index)[:-2])
            elif df.index.dtype == 'int64':
                ident = "00{}".format(str(index))
                # print('original:', index, '001:', ident)

            # add control field
            record.add_field(
                Field(
                    tag='001',
                    data=ident))

            for col in df:
                # if field is empty, skip
                if str(row[col]) == '':
                    continue
                # leader
                elif col == 'LDR':
                    l = list(record.leader)
                    l[0:5] = '0000'
                    l[5] = 'n'
                    l[6] = 'p'
                    if row['351'] == 'File Record' or 'Item Record':
                        l[7] = 'c'
                    else:
                        l[7] = 'd'
                    l[9] = 'a'  # flag saying this record is utf8
                    record.leader = "".join(l)
                    continue

                # 008
                elif col == '008':
                    field = Field(tag='008', data=row[col])

                # extract field name
                field = col[:3]

                # extract indicators
                if col.find('_') == -1 and len(col) < 5:
                    ind = [' ', ' ']
                elif col.find('_') == 3:
                    ind = [' ', ' ']
                elif col.find('_') == 4:
                    ind = [col[3], ' ']
                elif col.find('_') == 5:
                    ind = [' ', col[4]]
                else:
                    ind = [col[3], col[4]]

                # extract sub-fields
                subfields_data = list()
                subfields_prep = list(filter(None, row[col].split('$$')))
                for subfield in subfields_prep:
                    if subfield == '':
                        continue
                    subfields_data.append(subfield[0])
                    subfields_data.append(subfield[1:])

                print('field:', field)
                if not ind:
                    print('no indicators')
                else:
                    print('indicators:', ind)
                print('subfields:', subfields_data)

                record.add_field(
                    Field(
                        tag=field,
                        indicators=ind,
                        subfields=subfields_data))

            counter += 1
            writer.write(record)
        writer.close()
        run_time = time.time() - start_time

        return counter, run_time

    def create_marc_seq_file(self):
        """
        function to transform a MARC formatted Dataframe into a MARC sequantial file

        """
        df = self.full_catalog
        ad = AlphabetDetector()
        output_file_name = self.data_path_processed / (self.collection_id + '_final_' + self.dt_now + '.txt')

        with open(output_file_name, 'w', encoding="utf8") as f:
            for index, row in df.iterrows():
                if df.index.dtype == 'float64':
                    ident = "00{}".format(str(index)[:-2])
                elif df.index.dtype == 'int64':
                    ident = "00{}".format(str(index))

                f.write("{} {} {} {}".format(ident, "{:<5}".format('001'), 'L', ident) + '\n')
                for col in df:
                    # if field is empty, skip
                    if str(row[col]) == '':
                        continue

                    # check language
                    lang = ad.detect_alphabet(str(row[col]))
                    if 'HEBREW' in lang:
                        lang = 'H'
                    else:
                        lang = 'L'

                    # construct 5 character field code
                    if '_' in col:
                        col_name = "{:<5}".format(col[:col.find('_')])
                    else:
                        col_name = "{:<5}".format(col)

                    # construct the line for the MARC sequantial file
                    line = "{} {} {} {}".format(ident, col_name, lang, str(row[col]) + '\n')

                    # write to file
                    f.write(line)

    # def write_to_excel(self, path, sheets):
    #     """
    #     creates a excel file of a given dataframe
    #     :param self: the dateframe or a list of dataframes to write to excel
    #     :param path: the path name of the output file
    #     :param sheets: can be a list of sheet or
    #     """
    #     file_name = path / (self.collection_id + "_" + datetime.now() + '_preprocessing_test.xlsx')
    #     # Create a Pandas Excel writer using XlsxWriter as the engine.
    #     writer = pd.ExcelWriter(file_name, engine='xlsxwriter')
    #
    #     # Convert the dataframe to an XlsxWriter Excel object.
    #     if type(sheets) is list:
    #         i = 0
    #         for frame in self:
    #             frame.to_excel(writer, sheet_name=sheets[i])
    #             i += 1
    #     else:
    #         try:
    #             r

        # writer.close()

    def set_branch(self):
        while True:
            branch = input("Please enter the name of the Branch (Architect, Design, Dance, Theater): ")
            branch = str(branch)
            if branch[0].islower():
                branch = branch.capitalize()
            if branch not in Collection._project_branches:
                print('need to choose one of: Architect, Design, Dance, Theater')
                continue
            else:
                # we're happy with the value given.
                branch = 'VC-' + branch
                break

        self.branch = branch

    def set_collection_id(self):
        while True:
            collection_id = input("please enter the Collection ID:")
            if not collection_id:
                print("Please enter a collection ID.")
            else:
                # we're happy with the value given.
                break
            self.collection_id = collection_id

    def set_cms(self):
        while True:
            CMS = input("please enter the name of the target CMS (Aleph, Alma):")
            if not CMS or CMS.capitalize() not in ['Aleph', 'Alma']:
                print("Please enter the name of the target CMS (Aleph, Alma).")
            else:
                # we're happy with the value given.
                break
            self.CMS = CMS

    def clean_catalog(self):
        """
            initial cleanup of the row catalog
        """
        df_catalog = self.df_catalog.rename(columns={'סימול/מספר מזהה': 'סימול',
                                                     'סימול פרויקט': 'סימול'})
        df_catalog = df_catalog.fillna('')
        if df_catalog.iloc[0].str.contains('שדה חובה!!').any() or df_catalog.iloc[0].str.contains('שדה חובה').any():
            df_catalog = df_catalog[1:]
        return df_catalog


def write_log(text, log_file):
    f = open(log_file, 'a')  # 'a' will append to an existing file if it exists
    log_line = '[' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '] {}'.format(text)
    f.write("{}\n".format(text))  # write the text to the logfile and move to next line
    return
