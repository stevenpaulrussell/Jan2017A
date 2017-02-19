import os
import unittest

import action
import sentry
import setup_common_for_test
import cursors

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


    def test_archive_import_works(self):
        self.assertFalse(True)
        self.assertFalse('Am passing the append test in test_file_utilities')


    def test_archive_integrity_check_works(self):
        self.assertFalse(True)






if __name__ == '__main__':
    unittest.main()
