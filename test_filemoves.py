import unittest
import os
import shutil

import setup_common_for_test
import filemoves


test_directory = setup_common_for_test.read_test_locations()
imports_path = test_directory['imports_locator']


class MoveCopyAndDeleteUsingLocators(unittest.TestCase):
    def setUp(self):
        self.file_to_get = []

    def tearDown(self):
        for a_file_path in self.file_to_get:
            os.remove(a_file_path)

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

    def test_copy_alias_to_import_path_by_match_person_whole(self):
        to_match = dict(table='person', action='import whole', system='steve air')
        copy_path = filemoves.find_unique_import_directory_matching_pattern(imports_path, **to_match)
        copied_path = filemoves.copy_alias_to_path('person_table_example', test_directory, copy_path)
        self.file_to_get.append(copied_path)
        self.assertTrue(os.path.exists(copied_path))
        self.assertEqual(os.path.split(copied_path)[0], copy_path)

    def test_copy_file_path_to_dir_named_by_alias(self):
        """Takes file at copy_path_and_moves_to_alias_iff_alias_is_directory"""
        a_file_path = test_directory['table_as_query_cmds']
        print(a_file_path)
        copied_path = filemoves.copy_file_path_to_alias_named_directory(a_file_path, 'dropbox_test', test_directory)
        self.file_to_get.append(copied_path)
        source_name = os.path.split(a_file_path)[-1]
        copy_name = os.path.split(copied_path)[-1]
        self.assertEqual(source_name, copy_name)
        self.assertTrue(os.path.exists(copied_path))


    def test_remove_file_at_path(self):
        """Maybe have a trash store, and this copies to trash with time stamp then removes?"""


if __name__ == '__main__':
    unittest.main()
