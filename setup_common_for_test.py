import os

import file_utilities

test_source_path = '/Users/steve/TestItemsForJan2017A'
test_yaml_path = os.path.join(test_source_path, 'test_yaml_file')
test_directory_path = os.path.join(test_source_path, 'test_directory.xlsx')

yaml_test_dictionary = {'test_directory': test_directory_path}
test_directory = file_utilities.read_my_directory(yaml_test_dictionary['test_directory'])


def read_test_locations():
    test_locations = {}
    for alias, info in test_directory.items():
        test_locations[alias] = os.path.join(info['path'], info['filename'])
    return test_locations

