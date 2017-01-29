import unittest
import os.path

import setup_common_for_test
import filemoves


test_directory = setup_common_for_test.read_test_locations()
imports_path = test_directory['imports_locator']


class MoveCopyAndDeleteUsingLocators(unittest.TestCase):
    def test_can_get_import_paths_by_match(self):
        to_match = dict(table='person', action='import whole', system='steve air')
        result = filemoves.find_imports_directories_matching_rules(imports_path, **to_match)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['table'], 'person')
        self.assertTrue(os.path.exists(result[0]['path']))
        print(result[0]['path'])


    def xtest_can_move_test_files_by_alias_to_imports_by_path(self):
        result = filemoves.move_alias_to_path('person_table_example', test_directory, imports_path)
        self.assertEqual(True, result)


if __name__ == '__main__':
    unittest.main()
