import os
import unittest

import action
import file_utilities
import setup_common_for_test

test_directory = setup_common_for_test.read_test_locations()
imports_path = test_directory['imports_locator']


class MyTestCase(unittest.TestCase):
    def test_action_polls_all_directories_for_changes(self):
        work_list = action.poll_imports(test_directory['imports_locator'])
        if work_list:
            for work_item in work_list:
                (table, to_do, path, new, changed, missing) = work_item
                self.assertEqual(table, 'person')
                self.assertEqual(to_do, 'import whole')
                self.assertTrue(os.path.exists(path))
                print(table, path, new, changed, missing)
        else:
            print('No change')
            self.assertEqual(work_list, [])


if __name__ == '__main__':
    unittest.main()
