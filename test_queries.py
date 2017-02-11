import os
import unittest

import action
import setup_common_for_test
import dataqueda_constants
import file_utilities
import filemoves

path_to_listings = setup_common_for_test.read_test_locations()
imports_path = path_to_listings['imports_locator']
connect = dataqueda_constants.LOCAL


class TestRunQueries(unittest.TestCase):
    def do_person_import(self):
        to_match = dict(table='person', action='import whole', system='steve air')
        import_directory = filemoves.find_unique_import_directory_matching_pattern(imports_path, **to_match)
        filemoves.copy_alias_to_path('person_table_example', path_to_listings, import_directory)
        success, history = action.do_a_work_item(path_to_listings, connect=connect)
        self.assertTrue(success)
        # print('debug TestRunQueries.do_person_import', history)

    def setUp(self):
        setup_common_for_test.clean_directories()
        tables = action.get_current_tableset(connect=connect)
        action.destroy_database_tables(tables, connect=connect)
        action.make_database_tables(path_to_listings=path_to_listings, connect=connect)
        action.make_database_views(path_to_listings, connect=connect)
        self.do_person_import()
        self.reports_directory = path_to_listings['sql_reports']
        self.query_trouble_directory = path_to_listings['sql_query_trouble']

    def tearDown(self):
        setup_common_for_test.clean_directories()

    def test_prelim_can_get_needed_directories(self):
        actual_reports_directory, wildcard = os.path.split(self.reports_directory)
        actual_trouble_directory, file_name = os.path.split(self.query_trouble_directory)
        self.assertTrue(os.path.exists(actual_reports_directory))
        self.assertEqual(actual_reports_directory, actual_trouble_directory)
        self.assertEqual(wildcard, '*')
        self.assertEqual(file_name, 'sql_query_trouble')


    def xtest_good_queries_write_reports(self):
        #action.run_database_queries(path_to_listings, connect=dataqueda_constants.LOCAL)
        self.assertFalse('do this second')


    def xtest_bad_queries_write_trouble_reports(self):
        #action.run_database_queries(path_to_listings, connect=dataqueda_constants.LOCAL)
        self.assertFalse('do this second')

    def xtest_null_queries_remove_reports(self):
        #action.run_database_queries(path_to_listings, connect=dataqueda_constants.LOCAL)
        self.assertFalse('do this third')


if __name__ == '__main__':
    unittest.main()
