import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from shutil import copyfile

from VC_collections import drop_col_if_exists
import pandas as pd
from alphabet_detector import AlphabetDetector
from pymarc import XMLWriter, Record, Field

from .files import create_directory

project_branches = ['Architect', 'Dance', 'Design', 'Theater']


def initialize_logging(reports_path, collection_id):
    logging.basicConfig(level=logging.INFO,
                        filename=reports_path / (collection_id+'.log'),
                        filemode='w',
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%y-%m-%d %H:%M',
                        )
    logger = logging.getLogger(__name__)
    return logger


class Collection:

    def fetch_data(self):
        """
        :rtype: object

        """

        def get_works_sheet(xl, branch):
            works_sheets = [x for x in xl.sheet_names if 'יצירות' in x]
            if 'יצירות' in works_sheets:
                return 'יצירות'
            if 'Dance' in branch:
                assert ('יצירות - מחול' in xl.sheet_names), ' sheet יצירות - מחול does not exist in file.'
                return 'יצירות - מחול'
            elif 'Architect' in branch:
                assert ('יצירות - אדריכלות' in xl.sheet_names or 'יצירות' in xl.sheet_names),\
                    ' sheet יצירות - אדריכלות does not exist in file.'
                return 'יצירות - מחול'
            elif 'Theater' in branch:
                assert ('יצירות - תאטרון' in xl.sheet_names), ' sheet יצירות - תאטרון does not exist in file.'
                return 'יצירות - תאטרון'

            else:
                return ''

        def clean_raw_table(df_catalog):
            """
                initial cleanup of the row catalog
            :param df_catalog: the original fetched row collection catalog dataframe
            :return df_catalog: the cleaned collection catalog dataframe
            """
            df_catalog = df_catalog.rename(columns={'סימול/מספר מזהה': 'סימול'})
            df_catalog = df_catalog.fillna('')
            if df_catalog.iloc[0].str.contains('שדה חובה!!').any() or df_catalog.iloc[0].str.contains('שדה חובה').any():
                df_catalog = df_catalog[1:]
            return df_catalog

        def remove_unnecessary_columns(df_catalog):
            if 'סימול אב' in list(df_catalog.columns) and 'ROOTID' in list(df.columns):
                print("yes")
                df_catalog = drop_col_if_exists(df_catalog, 'ROOTID')

        def make_catalog_copy(file_path=None):
            for file in os.listdir(self.data_path_raw):
                filename = os.fsdecode(file)
                ext = Path(file).suffix

                if 'PRE_FINAL_aleph' in filename:  # this tests for substrings
                    file_path = os.path.join(self.data_path_raw, filename)
                    new_file = file_path.replace('_aleph', '')
                    copyfile(file_path, new_file)
                    return new_file


        xl = pd.ExcelFile(make_catalog_copy())
        assert ('קטלוג' in xl.sheet_names), logging.CRITICAL(f'קטלוג is not a sheet in {self.data_path_raw}')
        df_catalog = xl.parse('קטלוג')

        df_works_original = xl.parse(get_works_sheet(xl, self.branch))
        df_catalog = clean_raw_table(df_catalog)

        return df_catalog, df_works_original

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


        # create directory and sub-folders for collection
        self.BASE_PATH = Path.cwd() / ('VC-' + branch) / collection_id

        # initialize directory with all folder and sub-folders for the collection
        self.data_path, self.data_path_raw, self.data_path_processed, \
        self.data_path_reports, self.copyright_path, self.digitization_path, \
        self.authorities_path, self.aleph_custom21, self.aleph_manage18, \
        self.aleph_custom04 = create_directory(CMS, self.BASE_PATH)

        # set up logger for collection instance
        self.logger = initialize_logging(self.data_path_reports, collection_id)

        print(self.data_path, '\n', self.data_path_raw, '\n',self.data_path_processed,'\n', \
        self.data_path_reports,'\n', self.copyright_path, '\n',self.digitization_path, '\n',\
        self.authorities_path,'\n', self.aleph_custom21,'\n', self.aleph_manage18, '\n',\
        self.aleph_custom04)

        self.df_catalog, self.df_works_original = self.fetch_data()



    def create_MARC_XML(self, branch, collection_id, dt_now=datetime.now()):
        """
        Creates a MARC XML format file from the given dataframe
        :param dt_now:
        :param branch: The project branch (Architect, Dance, Design, Theater)
        :param collection_id: The Collection ID (call number)
        :param self: the modiefied
        """
        output_file = Path.cwd() / branch / collection_id / 'Data' / 'Processed' / (
                collection_id + '_final_' + dt_now + ".xml")
        writer = XMLWriter(open(output_file, 'wb'))
        start_time = time.time()
        counter = 1

        for index, row in self.iterrows():

            record = Record()

            if self.index.dtype == 'float64':
                ident = "00{}".format(str(index)[:-2])
            elif self.index.dtype == 'int64':
                ident = "00{}".format(str(index))
                # print('original:', index, '001:', ident)

            # add control field
            record.add_field(
                Field(
                    tag='001',
                    data=ident))

            for col in self:
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

                # extract subfields
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

    def create_marc_seq_file(df, collection_id, path):
        """
        function to transform a MARC formatted Dataframe into a MARC sequantial file
        :param collection_id:  The Collection ID Ca
        :param df: The Dataframe to transform to MARC sequantial file
        :param path:
        """

        ad = AlphabetDetector()

        with open(os.path.join(path, collection_id + '_finalAleph_' + dt_now + '.txt'), 'w', encoding="utf8") as f:
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

    def write_to_excel(df, path, sheets):
        """
        creates a excel file of a given dataframe
        :param df: the dateframe or a list of dataframes to write to excel
        :param path: the path name of the output file, or a list of sheets
        :param sheets: can be a list of sheet or
        """

        # Create a Pandas Excel writer using XlsxWriter as the engine.
        writer = pd.ExcelWriter(path, engine='xlsxwriter')

        # Convert the dataframe to an XlsxWriter Excel object.
        if type(df) is list and type(sheets) is list:
            i = 0
            for frame in df:
                frame.to_excel(writer, sheet_name=sheets[i])
                i += 1
        else:
            df.to_excel(writer, sheet_name=sheets)

        writer.close()

    def set_branch(self):
        while True:
            branch = input("Please enter the name of the Branch (Architect, Design, Dance, Theater): ")
            branch = str(branch)
            if branch[0].islower():
                branch = branch.capitalize()
            if branch not in project_branches:
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
                print("Please enter a collectionID.")
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


def write_log(text, log_file):
    f = open(log_file, 'a')  # 'a' will append to an existing file if it exists
    log_line = '[' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '] {}'.format(text)
    f.write("{}\n".format(text))  # write the text to the logfile and move to next line
    return
