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
import pathlib
from VC_collections.Collection import Collection
from VC_collections.columns import drop_col_if_exists

import timeit

from VC_collections.files import get_branch_colletionID


def main():
    start_time = timeit.default_timer()
    print(get_branch_colletionID())
    # collection = Collection()


if __name__ == '__main__':
    main()