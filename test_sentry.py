import os
import time
import unittest

import sentry
import file_utilities
import setup_common_for_test


dropbox_directory_path = file_utilities.get_path_from_alias('dropbox_test_directory')
TEMP_FILE_NAME = 'temp_file_name'


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
    def setUp(self):
        setup_common_for_test.clean_directories()
        sentry.poll_imports()
        sentry.work_list = []

    def tearDown(self):
        setup_common_for_test.clean_directories()


    def test_action_polls_all_directories_for_changes_sees_no_changes_if_are_none(self):
        sentry.path_to_listings = setup_common_for_test.test_directory
        sentry.work_list = []
        sentry.poll_imports()
        self.assertFalse(sentry.work_list)

    def test_action_polls_all_directories_for_changes_does_see_changes(self):
        dest_path = file_utilities.get_path_from_alias('import whole person directory')
        source_path = file_utilities.get_path_from_alias('person_table_example')
        file_utilities.copy_file_path_to_dir(source_path, dest_path)
        sentry.poll_imports()
        self.assertEqual(len(sentry.work_list), 1 )
        work_item = sentry.work_list[0]
        self.assertEqual(work_item.table_name, 'person')
        self.assertEqual(work_item.action, 'import whole')


if __name__ == '__main__':
    unittest.main()
