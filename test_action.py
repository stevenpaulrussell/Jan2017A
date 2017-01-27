import os
import unittest

import action
import file_utilities
import setup_common_for_test

test_directory = setup_common_for_test.read_test_locations()
imports_path = test_directory['imports_locator']


class MyTestCase(unittest.TestCase):
    def test_action_polls_all_directories_for_changes(self):
        action.poll_imports(test_directory['imports_locator'])
        if action.work_list:
            print('Seeing {} work items'.format(len(action.work_list)))
            for work_item in action.work_list:
                self.assertEqual(work_item.table_name, 'person')
                self.assertEqual(work_item.to_do, 'import whole')
                self.assertIn(work_item.file_change, ('new', 'missing'))
                if work_item.file_change == 'new':
                    self.assertTrue(os.path.exists(work_item.path))
        else:
            print('No change')


if __name__ == '__main__':
    unittest.main()
