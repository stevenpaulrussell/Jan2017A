import os
import time
import unittest

import setup_common_for_test
import sentry


dropbox_directory_path = setup_common_for_test.test_directory['dropbox_test']['path']
temp_name = 'temp_name'

class SmokeAndLearningiTestCase(unittest.TestCase):
    def setUp(self):
        self.assertTrue(os.path.exists(dropbox_directory_path))
        self.temp_path = os.path.join(dropbox_directory_path, temp_name)

    def tearDown(self):
        try:
            os.remove(self.temp_path)
        except FileNotFoundError:
            pass


    def make_a_file(self, file_name=temp_name):
        path = os.path.join(dropbox_directory_path, file_name)
        with open(path, 'w') as fp:
            fp.write('hello\n')

    def test_can_create_files_in_dropbox_and_get_info(self):
        self.make_a_file()
        self.assertTrue(os.path.exists(self.temp_path))

    def test_can_get_file_stats(self):
        self.make_a_file()
        made = os.stat(self.temp_path).st_mtime
        time.sleep(2)
        with open(self.temp_path, 'a') as fp:
            fp.write('goodbye\n')
        changed = os.stat(self.temp_path).st_mtime
        lapsed = changed - made  # Python os.stat docs say that .st_mtime has a two second granularity
        self.assertTrue(lapsed > 1)
        self.assertTrue(lapsed < 3)


class TestSentryGetsFileChanges(unittest.TestCase):
    def setUp(self):
        self.assertTrue(os.path.exists(dropbox_directory_path))
        self.temp_path = os.path.join(dropbox_directory_path, temp_name)

    def tearDown(self):
        file_names = next(os.walk(dropbox_directory_path))[-1]
        for file_name in file_names:
            os.remove(os.path.join(dropbox_directory_path, file_name))


    def make_a_file(self, file_name=temp_name):
        path = os.path.join(dropbox_directory_path, file_name)
        with open(path, 'w') as fp:
            fp.write('hello\n')

    def test_can_see_files_and_dirs_in_sentry(self):
        self.make_a_file()
        self.make_a_file('.sentry')
        file_dictionary = sentry.get_current_file_stats(dropbox_directory_path)
        self.assertEqual(sentry.previous_file_data, {})
        self.assertIn(temp_name, file_dictionary)
        self.assertIn('.sentry', file_dictionary)

    def test_load_json_from_dot_sentry_returns_None_if_no_dot_sentry(self):
        sentry.dump_json_to_dot_sentry(dropbox_directory_path)
        sentry.load_json_from_dot_sentry(dropbox_directory_path)
        self.assertEqual(sentry.previous_file_data, {})

    def test_dump_json_from_dot_sentry_returns_None_if_no_dot_sentry(self):
        sentry.dump_json_to_dot_sentry(dropbox_directory_path)
        sentry.load_json_from_dot_sentry(dropbox_directory_path)
        self.assertEqual(sentry.previous_file_data, {})

    def test_sentry_take_roll_of_new_changes_and_missing_finds_nothing_with_nothing_in(self):
        new, changed, missing = sentry.take_roll_of_new_changes_and_missing(dropbox_directory_path)
        self.assertEqual(new, set())
        self.assertEqual(missing, set())

    def test_sentry_take_roll_of_new_changes_and_missing_finds_two_new_files(self):
        self.make_a_file()
        self.make_a_file('.sentry')
        new, changed, missing = sentry.take_roll_of_new_changes_and_missing(dropbox_directory_path)
        self.assertIn('temp_name', new)
        self.assertIn('.sentry', new)
        self.assertEqual(changed, set())
        self.assertEqual(missing, set())

if __name__ == '__main__':
    unittest.main()
