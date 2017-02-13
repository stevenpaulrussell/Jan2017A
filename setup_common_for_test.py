import os
import shutil

import file_utilities


TEST_SOURCE_PATH = '/Users/steve/Test2017B'
LOCATOR_NAME = 'locator_for_test.xlsx'


file_utilities.read_file_listings(os.path.join(TEST_SOURCE_PATH, LOCATOR_NAME))
test_directory = file_utilities.file_listings

CLEANS = ('sql_reports_directory',
          'archive_directory',
          'archive_directory/person',
          'import whole person directory',
          'import lines person directory',
          )

def clean_directories(verbose=False):
    def vprint(astring):
        if verbose:
            print(astring)

    vprint('\n{}\nClean directories in test_locations in setup_common_for_test'.format('*'*8))
    for alias in CLEANS:
        directory_path = file_utilities.get_path_from_alias(alias)
        vprint('\n\t{}'.format(alias))
        this_path, dirs, files = os.walk(directory_path).__next__()
        assert this_path == directory_path
        for filename in files:
            if filename[0] in ('.', '~') and filename != '.sentry':
                vprint('\t\tSkipping {}'.format(filename, ))
                continue
            filepath = os.path.join(directory_path, filename)
            os.remove(filepath)
            vprint('\t\tx -> {}'.format(filename, ))
    vprint('\nDone with clean directories in test_locations in setup_common_for_test\n{}\n'.format('*'*8))


