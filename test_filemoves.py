import unittest
import os.path

import setup_common_for_test
import filemoves


test_directory = setup_common_for_test.read_test_locations()
imports_path = test_directory['imports_locator']


class MoveCopyAndDeleteUsingLocators(unittest.TestCase):
    def test_can_get_import_paths_by_match(self):
        to_match = dict(table='person', action='import whole', system='steve air')
        result = filemoves.find_all_imports_lines_matching_pattern(imports_path, **to_match)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['table'], 'person')
        self.assertTrue(os.path.exists(result[0]['path']))

    def test_can_get_unique_import_path_by_match(self):
        to_match = dict(table='person', action='import whole', system='steve air')
        path = filemoves.find_unique_import_directory_matching_pattern(imports_path, **to_match)
        self.assertTrue(os.path.exists(path))

    def test_copy_alias_to_path(self):
        to_match = dict(table='person', action='import whole', system='steve air')
        copy_path = filemoves.find_unique_import_directory_matching_pattern(imports_path, **to_match)
        result = filemoves.copy_alias_to_path('person_table_example', test_directory, copy_path)



if __name__ == '__main__':
    unittest.main()
