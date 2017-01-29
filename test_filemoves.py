import unittest

import setup_common_for_test
import filemoves


test_directory = setup_common_for_test.read_test_locations()
imports_path = test_directory['imports_locator']


class MoveCopyAndDeleteUsingLocators(unittest.TestCase):
    def test_can_move_test_files_by_alias_to_imports_by_path(self):
        result = filemoves.move_alia_to_path('person_table_example', test_directory, imports_path)
        self.assertEqual(True, result)


if __name__ == '__main__':
    unittest.main()
