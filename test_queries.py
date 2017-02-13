import os
import unittest

import action
import setup_common_for_test
import dataqueda_constants
import file_utilities

LOCAL = dataqueda_constants.LOCAL


class TestRunQueries(unittest.TestCase):
    def setUp(self):
        setup_common_for_test.clean_directories()

        tables = action.get_current_tableset(connect=LOCAL)
        action.destroy_database_tables(tables, connect=LOCAL)
        action.make_database_tables(connect=LOCAL)
        action.make_database_views(connect=LOCAL)

        test_file_path = file_utilities.get_path_from_alias('person_table_example')
        destination_directory = file_utilities.get_path_from_alias('import whole person directory')
        file_utilities.copy_file_path_to_dir(test_file_path, destination_directory)
        success, history = action.do_a_work_item(connect=LOCAL)
        self.assertTrue(success)

    def tearDown(self):
        pass
        #setup_common_for_test.clean_directories()

    def test_good_queries_write_reports(self):
        success, history = action.run_database_queries(connect=LOCAL)
        self.assertTrue(success)


    def xtest_bad_queries_write_trouble_reports(self):
        #action.run_database_queries(path_to_listings, connect=LOCAL)
        self.assertFalse('do this second')

    def xtest_null_queries_remove_reports(self):
        #action.run_database_queries(path_to_listings, connect=LOCAL)
        self.assertFalse('do this third')


if __name__ == '__main__':
    unittest.main()
