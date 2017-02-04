import os
import time
import unittest

import setup_common_for_test
import sentry


dropbox_directory_path = setup_common_for_test.test_directory['dropbox_test']['path']
TEMP_FILE_NAME = 'temp_file_name'
test_directory = setup_common_for_test.read_test_locations()
imports_path = test_directory['imports_locator']


class TestSentryGetsFileChanges(unittest.TestCase):
    def setUp(self):
        self.assertTrue(os.path.exists(dropbox_directory_path))
        self.temp_path = os.path.join(dropbox_directory_path, TEMP_FILE_NAME)
        sentry.load_json_from_sentry_file(self.temp_path)

    def tearDown(self):
        file_names = next(os.walk(dropbox_directory_path))[-1]
        for file_name in file_names:
            os.remove(os.path.join(dropbox_directory_path, file_name))
        sentry.previous_file_data = {}

    def make_temp_file(self):
        path = os.path.join(dropbox_directory_path, TEMP_FILE_NAME)
        with open(path, 'w') as fp:
            fp.write('hello\n')

    def test_can_see_files_and_dirs_in_sentry(self):
        self.make_temp_file()
        previous_file_data = sentry.load_json_from_sentry_file(dropbox_directory_path)
        file_dictionary = sentry.get_current_file_stats(dropbox_directory_path)
        self.assertEqual(previous_file_data, {})
        self.assertIn('temp_file_name', file_dictionary)
        self.assertNotIn(sentry.SENTRY_FILE_NAME, file_dictionary)  #This one is ignored

    def test_dump_json_from_dot_sentry_returns_None_if_no_dot_sentry(self):
        sentry.load_json_from_sentry_file(dropbox_directory_path)
        self.assertEqual(sentry.previous_file_data, {})

    def test_sentry_take_roll_of_new_changes_and_missing_finds_nothing_with_nothing_in(self):
        new, changed, missing = sentry.take_roll_of_new_changes_and_missing(dropbox_directory_path)
        self.assertEqual(new, set())
        self.assertEqual(missing, set())

    def test_sentry_take_roll_of_new_changes_and_missing_finds_one_new_file(self):
        self.make_temp_file()
        new, changed, missing = sentry.take_roll_of_new_changes_and_missing(dropbox_directory_path)
        self.assertIn(TEMP_FILE_NAME, new)
        self.assertEqual(changed, set())
        self.assertEqual(missing, set())

    def test_sentry_finds_changes(self):
        self.make_temp_file()
        new, changed, missing = sentry.take_roll_of_new_changes_and_missing(dropbox_directory_path)
        self.assertIn(TEMP_FILE_NAME, new)
        self.assertNotIn(sentry.SENTRY_FILE_NAME, new)  #This one is ignored
        self.assertEqual(changed, set())
        self.assertEqual(missing, set())
        time.sleep(3)
        with open(self.temp_path, 'a') as fp:
            fp.write('goodbye\n')
        new, changed, missing = sentry.take_roll_of_new_changes_and_missing(dropbox_directory_path)
        self.assertEqual(new, set())
        self.assertIn(TEMP_FILE_NAME, changed)
        self.assertEqual(missing, set())


class MyTestCase(unittest.TestCase):
    def test_action_polls_all_directories_for_changes(self):
        sentry.path_to_listings = test_directory
        sentry.poll_imports()
        if sentry.changed_list:
            print('Seeing {} work items'.format(len(sentry.changed_list)))
            for work_item in sentry.changed_list:
                self.assertEqual(work_item.table_name, 'person')
                self.assertEqual(work_item.to_do, 'import whole')
                self.assertIn(work_item.file_change, ('new', 'missing'))
                if work_item.file_change == 'new':
                    file_path = os.path.join(work_item.directory, work_item.file_name)
                    self.assertTrue(os.path.exists(file_path))
        else:
            print('No change')


if __name__ == '__main__':
    unittest.main()
