import os

import file_utilities

test_source_path = '/Users/steve/TestItemsForJan2017A'

#Following hardcoded here instead of in test_directory.  Reason is that these are used to test functions needed for
# test_directory to be read

test_bad_header_spreadsheet_path = os.path.join(test_source_path, 'bad_header_spreadsheet_test.xls')
test_header_only_spreadsheet_path = os.path.join(test_source_path, 'header_only_spreadsheet_test.xls')
test_various_problems_spreadsheets_path = os.path.join(test_source_path, 'various_problems_spreadsheet_test.xls')
test_empty_spreadsheet_path = os.path.join(test_source_path, 'empty_spreadsheet_test.xls')


file_utilities.read_file_listings(os.path.join(test_source_path, 'test_directory.xlsx'))
test_directory = file_utilities.file_listings


def read_test_locations():
    assert os.path.exists(test_source_path)
    assert os.path.exists(test_bad_header_spreadsheet_path)
    assert os.path.exists(test_header_only_spreadsheet_path)
    assert os.path.exists(test_various_problems_spreadsheets_path)
    assert os.path.exists(test_empty_spreadsheet_path)
    test_locations = {}
    for alias, info in test_directory.items():
        test_locations[alias] = os.path.join(info['path'], info['filename'])
    return test_locations


