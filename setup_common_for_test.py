import os

import file_utilities


TEST_SOURCE_PATH = '/Users/steve/Test2017B'
LOCATOR_NAME = 'locator_for_test.xlsx'


file_utilities.read_file_listings(os.path.join(TEST_SOURCE_PATH, LOCATOR_NAME))
test_directory = file_utilities.file_listings


# def read_test_locations():
#     test_locations = {}
#     for alias, info in test_directory.items():
#         test_locations[alias] = os.path.join(info['path'], info['filename'])
#     return test_locations
#

def clean_directories(verbose=False):
    def vprint(astring):
        if verbose:
            print(astring)

    vprint('\n{}\nClean directories in test_locations in setup_common_for_test'.format('*'*8))
    keepers = set()
    for alias, details in test_directory.items():
        if details['filename'] != '*':
            keepers.add(os.path.join(details['path'], details['filename']))
    for alias, details in test_directory.items():
        if details['filename'] == '*':
            a_path = details['path']
            vprint('\n\t{}'.format(alias))
            this_path, dirs, files = os.walk(a_path).__next__()
            for filename in files:
                if filename[0] in ('.', '~'):
                    vprint('\t\tSkipping {}'.format(filename, ))
                    continue
                filepath = os.path.join(this_path, filename)
                if filepath in keepers:
                    vprint('\t\t*** Skipping {}.  Is in Keepers!!'.format(filename, ))
                    continue
                os.remove(filepath)
                vprint('\t\tx -> {}'.format(filename, ))
    vprint('\nClean imports directories')
    path_to_listings = read_test_locations()
    imports_path = path_to_listings['imports_locator']
    imports_gen = file_utilities.spreadsheet_keyvalue_generator(imports_path)
    for location in imports_gen:
        directory_path = location['path']
        vprint('\n\t{}'.format(directory_path))
        this_path, dirs, files = os.walk(directory_path).__next__()
        for filename in files:
            if filename[0] in ('.', '~') and filename != '.sentry':
                vprint('\t\tSkipping {}'.format(filename, ))
                continue
            filepath = os.path.join(this_path, filename)
            if filepath in keepers:
                vprint('\t\t*** Skipping {}.  Is in Keepers!!'.format(filename, ))
                continue
            os.remove(filepath)
            vprint('\t\tx -> {}'.format(filename, ))
    vprint('\nDone with clean directories in test_locations in setup_common_for_test\n{}\n'.format('*'*8))


