import os
import unittest

import action
import sentry
import setup_common_for_test

import dataqueda_constants
import file_utilities
from dataqueda_constants import LOCAL


class CanProperlyHandleWholeTableImports(unittest.TestCase):
    def setUp(self):
        setup_common_for_test.clean_directories()
        tableset = action.get_current_tableset(connect=LOCAL)
        action.destroy_database_tables(tableset, connect=LOCAL)
        action.make_database_tables(connect=dataqueda_constants.LOCAL)
        action.make_database_views(connect=dataqueda_constants.LOCAL)
        sentry.poll_imports()
        sentry.work_list = []
        dest_path = file_utilities.get_path_from_alias('import whole person directory')
        source_path = file_utilities.get_path_from_alias('person_table_example')
        file_utilities.copy_file_path_to_dir(source_path, dest_path)

    def tearDown(self):
        sentry.poll_imports()
        sentry.work_list = []
        tableset = action.get_current_tableset(connect=dataqueda_constants.LOCAL)
        if tableset:
            action.destroy_database_tables(tableset, connect=dataqueda_constants.LOCAL)
        setup_common_for_test.clean_directories()


    def test_doing_whole_table_import_appends_data_to_archive_import_directory(self):
        sentry.poll_imports()
        success, history = action.do_a_work_item(connect=dataqueda_constants.LOCAL)
        self.assertTrue(success)
        archive_import_locator_path = file_utilities.get_path_from_alias('archive_import_locator')
        apath = file_utilities.get_path_from_alias('person_table_example')
        expected_file_name = os.path.split(apath)[-1]
        expected_line = next(file_utilities.spreadsheet_keyvalue_generator(archive_import_locator_path))
        print('debug in test_archive_functions', expected_line)

        self.assertIn(expected_file_name, expected_line['filename'])


    def test_one_line_insert(self):
        self.assertFalse('Have tested one line imports both virgin and post-virgin')



    def test_importing_from_archive_works(self):
        self.assertFalse(True)


    def test_archive_integrity_check_works(self):
        self.assertFalse(True)






if __name__ == '__main__':
    unittest.main()
