import os

import file_utilities

test_source_path = '/Users/steve/TestItemsForJan2017A'
test_yaml_path = os.path.join(test_source_path, 'test_yaml_file')
test_directory_path = os.path.join(test_source_path, 'test_directory.xlsx')

yaml_test_dictionary = {'test_directory': test_directory_path}


def read_test_locations():
    my_gen = file_utilities.spreadsheet_keyvalue_generator(test_directory_path)
    my_directory = {}
    for aline in my_gen:
        alias = aline.pop('alias')
        assert aline['system'] == 'steve air'
        my_directory[alias] = os.path.join(aline['path'], aline['filename'])
    return my_directory

