import os


def make_sure_path_exists(path):
    """
    Make sure Path exists. raises an exception if path doesn't exist

    :param path: the path to check
    """

    if not os.path.exists(path):
        os.makedirs(path)


def create_directory(CMS, branch, collectionID):
    """
                reate Directory structure
            :param branch: the brach name (Architect, Dance, Design or Theater)
            :param collectionID: the ID of the collection
            :return: returns the paths to the directories that were created:
                    data_path, data_path_raw, data_path_processed,
                    data_path_reports, copyright_path, digitization_path,
                    authorities_path, aleph_custom21, aleph_manage18, aleph_custom04

            """
    # create a Data Folder

    base_path = Path.cwd() / branch / collectionID

    data_path = base_path / 'Data'
    make_sure_path_exists(data_path)

    # create a Data Folder
    data_path_raw = data_path / 'raw'
    make_sure_path_exists(data_path_raw)

    # create a Data Folder
    data_path_processed = data_path / 'processed'
    make_sure_path_exists(data_path_processed)

    # create a Data Folder
    data_path_reports = data_path / 'reports'
    make_sure_path_exists(data_path_reports)

    # create a Copyright folder
    copyright_path = base_path / 'Copyright'
    make_sure_path_exists(copyright_path)

    # create a Digitization folder
    digitization_path = base_path / 'Digitization'
    make_sure_path_exists(digitization_path)

    # create a Authorities folder
    authorities_path = base_path / 'Authorities'
    make_sure_path_exists(authorities_path)

    # create a custom21 folder
    aleph_custom21 = base_path / 'Custom21'
    make_sure_path_exists(aleph_custom21)

    # create a custom21 folder
    aleph_manage18 = base_path / 'Manage18'
    make_sure_path_exists(aleph_manage18)

    # create a custom04 folder
    if CMS == 'aleph':
        aleph_custom04 = base_path / 'Custom04'
    else:
        aleph_custom04 = base_path / 'Custom04' / 'Alma'
    make_sure_path_exists(aleph_custom04)

    var = data_path, data_path_raw, data_path_processed, data_path_reports, \
          copyright_path, digitization_path, authorities_path, aleph_custom21, \
          aleph_manage18, aleph_custom04
    return var
