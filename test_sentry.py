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
        try:
            os.remove(self.temp_path)
        except FileNotFoundError:
            pass

    def make_a_file(self, file_name=temp_name):
        path = os.path.join(dropbox_directory_path, file_name)
        with open(path, 'w') as fp:
            fp.write('hello\n')

    def test_can_see_files_and_dirs_in_sentry(self):
        self.make_a_file()
        self.make_a_file('.sentry')
        dirs, files = sentry.get_file_stats(dropbox_directory_path)
        self.assertEqual(sentry.file_stats, {'default': 'should not be seen'})
        self.assertEqual(dirs, [])
        self.assertIn(temp_name, files)
        self.assertIn('.sentry', files)

    def test_load_json_from_dot_sentry_returns_None_if_no_dot_sentry(self):
        sentry.load_json_from_dot_sentry(dropbox_directory_path)
        self.assertEqual(sentry.file_stats, {})

    def test_dump_json_from_dot_sentry_returns_None_if_no_dot_sentry(self):
        sentry.load_json_from_dot_sentry(dropbox_directory_path)
        self.assertEqual(sentry.file_stats, {})

if __name__ == '__main__':
    unittest.main()
