import numpy as np
import csv
import os
import pandas as pd
import math
import re
import errno
from collections import defaultdict, Counter
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import pprint
from anytree import Node, RenderTree
from anytree.exporter import DotExporter
from datetime import datetime
import sys
import shutil
from alphabet_detector import AlphabetDetector
import difflib

from pathlib import Path
from VC_collections.Files import make_sure_path_exists

project_branches = ['Architect', 'Dance', 'Design', 'Theater']


class Collection:

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
        self.log_file = None

        # create directory and sub-folders for collection
        self.BASE_PATH = Path.cwd() / ('VC-' + branch) / collection_id

        self.data_path, self.data_path_raw, self.data_path_processed, \
        self.data_path_reports, self.copyright_path, self.digitization_path, \
        self.authorities_path, self.aleph_custom21, self.aleph_manage18, self.aleph_custom04 = create_directory(CMS, collection_id, branch)

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
