import os
import time
import unittest

import setup_common_for_test


dropbox_directory_info = setup_common_for_test.test_directory['dropbox_test']


class SmokeAndLearningiTestCase(unittest.TestCase):
    def setUp(self):
        self.assertTrue(os.path.exists(dropbox_directory_info['path']))
        self.temp_name = 'temp_name'
        self.temp_path = os.path.join(dropbox_directory_info['path'], self.temp_name)
        if os.path.exists(self.temp_path):
            os.remove(self.temp_path)

    def tearDown(self):
        os.remove(self.temp_path)

    def make_a_file(self):
        with open(self.temp_path, 'w') as fp:
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

if __name__ == '__main__':
    unittest.main()
