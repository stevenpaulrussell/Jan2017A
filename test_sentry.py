import os
import time
import unittest

import setup_common_for_test
import sentry


dropbox_directory_path = setup_common_for_test.test_directory['dropbox_test']['path']
temp_name = 'temp_name'


class TestSentryGetsFileChanges(unittest.TestCase):
    def setUp(self):
        self.assertTrue(os.path.exists(dropbox_directory_path))
        self.temp_path = os.path.join(dropbox_directory_path, temp_name)
        sentry.load_json_from_dot_sentry(self.temp_path)

    def tearDown(self):
        file_names = next(os.walk(dropbox_directory_path))[-1]
        for file_name in file_names:
            os.remove(os.path.join(dropbox_directory_path, file_name))
        sentry.previous_file_data = {}

    def make_a_file(self, file_name=temp_name):
        path = os.path.join(dropbox_directory_path, file_name)
        with open(path, 'w') as fp:
            fp.write('hello\n')

    def test_can_see_files_and_dirs_in_sentry(self):
        self.make_a_file()
        previous_file_data = sentry.load_json_from_dot_sentry(dropbox_directory_path)
        file_dictionary = sentry.get_current_file_stats(dropbox_directory_path)
        self.assertEqual(previous_file_data, {})
        self.assertIn(temp_name, file_dictionary)
        self.assertNotIn('.sentry', file_dictionary)  #This one is ignored

    def test_dump_json_from_dot_sentry_returns_None_if_no_dot_sentry(self):
        sentry.load_json_from_dot_sentry(dropbox_directory_path)
        self.assertEqual(sentry.previous_file_data, {})

    def test_sentry_take_roll_of_new_changes_and_missing_finds_nothing_with_nothing_in(self):
        new, changed, missing = sentry.take_roll_of_new_changes_and_missing(dropbox_directory_path)
        self.assertEqual(new, set())
        self.assertEqual(missing, set())

    def test_sentry_take_roll_of_new_changes_and_missing_finds_one_new_file(self):
        self.make_a_file()
        new, changed, missing = sentry.take_roll_of_new_changes_and_missing(dropbox_directory_path)
        self.assertIn('temp_name', new)
        self.assertEqual(changed, set())
        self.assertEqual(missing, set())

    def test_sentry_finds_changes(self):
        self.make_a_file()
        new, changed, missing = sentry.take_roll_of_new_changes_and_missing(dropbox_directory_path)
        self.assertIn('temp_name', new)
        self.assertNotIn('.sentry', new)  #This one is ignored
        self.assertEqual(changed, set())
        self.assertEqual(missing, set())
        time.sleep(3)
        with open(self.temp_path, 'a') as fp:
            fp.write('goodbye\n')
        new, changed, missing = sentry.take_roll_of_new_changes_and_missing(dropbox_directory_path)
        self.assertEqual(new, set())
        self.assertIn('temp_name', changed)
        self.assertEqual(missing, set())
 

if __name__ == '__main__':
    unittest.main()
