import unittest
import os

import dataqueda_constants
import filemoves
import file_utilities
import action
import setup_common_for_test

connect = dataqueda_constants.LOCAL
path_to_listings = setup_common_for_test.read_test_locations()
imports_path = path_to_listings['imports_locator']


class RebuildDatabaseFromBaseDocuments(unittest.TestCase):
    def test_can_destroy_and_rebuild_tables(self):
        tables = action.get_current_tableset(connect=connect)
        action.destroy_database_tables(tables, connect=connect)

        successt, historyt = action.make_database_tables(path_to_listings=path_to_listings, connect=connect)
        successv, historyv = action.make_database_views(path_to_listings=path_to_listings, connect=connect)
        tables = action.get_current_tableset(connect=connect)
        (first_command, vars), first_psycop_response = historyv[0]

        self.assertTrue(successt)
        self.assertTrue(successv)
        self.assertIn('person', tables)
        self.assertIn('CREATE VIEW', first_command)


class InsertFromImportsSimple(unittest.TestCase):
    def setUp(self):
        setup_common_for_test.clean_directories(verbose=True)
        tables = action.get_current_tableset(connect=connect)
        action.destroy_database_tables(tables, connect=connect)
        action.make_database_tables(path_to_listings=path_to_listings, connect=connect)
        action.make_database_views(path_to_listings, connect=connect)

    def tearDown(self):
        setup_common_for_test.clean_directories()


    def test_can_import_whole_sheet(self):
        to_match = dict(table='person', action='import whole', system='steve air')
        import_directory = filemoves.find_unique_import_directory_matching_pattern(imports_path, **to_match)
        spreadsheet_path = filemoves.copy_alias_to_path('person_table_example', path_to_listings, import_directory)
        spreadsheet_name = os.path.split(spreadsheet_path)[-1]
        success_dir_wildcarded = path_to_listings['archive/person']
        success_dir = success_dir_wildcarded[:-2]
        success_path = os.path.join(success_dir, spreadsheet_name)

        success, history = action.do_a_work_item(path_to_listings, connect=connect)
        (first_command, vars), first_psycop_response = history[0]
        value_mapping_as_dict = vars[0]

        self.assertTrue(success)
        self.assertIn('INSERT INTO', first_command)
        self.assertTrue(value_mapping_as_dict.keys())
        self.assertFalse(os.path.exists(spreadsheet_path))  # import should have been removed
        self.assertTrue(os.path.exists(success_path))  # successful import copied here for safety


    def test_failure_import_whole_sheet(self):
        to_match = dict(table='person', action='import whole', system='steve air')
        import_directory = filemoves.find_unique_import_directory_matching_pattern(imports_path, **to_match)
        spreadsheet_path = filemoves.copy_alias_to_path('person_table_example', path_to_listings, import_directory)
        spreadsheet_name = os.path.split(spreadsheet_path)[-1]
        success_dir_wildcarded = path_to_listings['archive/person']
        success_directory = success_dir_wildcarded[:-2]
        success_path = os.path.join(success_directory, spreadsheet_name)
        fail_file_name = 'ErRoR_{}'.format(spreadsheet_name)
        fail_path = os.path.join(import_directory, fail_file_name)

        action.do_a_work_item(path_to_listings, connect=connect)
        os.remove(success_path)
        should_be_None = action.do_a_work_item(path_to_listings, connect=connect)
        filemoves.copy_alias_to_path('person_table_example', path_to_listings, import_directory)

        success, history = action.do_a_work_item(path_to_listings, connect=connect)

        (first_command, vars), first_psycop_response = history[0]
        value_mapping_as_dict = vars[0]

        self.assertFalse(should_be_None)
        self.assertFalse(success)
        self.assertIn('INSERT INTO', first_command)
        self.assertTrue(value_mapping_as_dict.keys())
        self.assertTrue(os.path.exists(spreadsheet_path))  # import is not removed
        self.assertTrue(os.path.exists(fail_path))  # failure rewrites the import


class InsertFromImportsIncrementally(unittest.TestCase):
    def setUp(self):
        setup_common_for_test.clean_directories()
        tables = action.get_current_tableset(connect=connect)
        action.destroy_database_tables(tables, connect=connect)
        action.make_database_tables(path_to_listings=path_to_listings, connect=connect)
        action.make_database_views(path_to_listings, connect=connect)

    def tearDown(self):
        setup_common_for_test.clean_directories()

    def test_incremental_with_errors(self):
        to_match = dict(table='person', action='import by line', system='steve air')
        import_directory = filemoves.find_unique_import_directory_matching_pattern(imports_path, **to_match)
        spreadsheet_path = filemoves.copy_alias_to_path('person_draft_error', path_to_listings, import_directory)
        spreadsheet_name = os.path.split(spreadsheet_path)[-1]
        success_dir_wildcarded = path_to_listings['archive/person']
        success_dir = success_dir_wildcarded[:-2]
        success_path = os.path.join(success_dir, spreadsheet_name)

        success, history = action.do_a_work_item(path_to_listings, connect=connect)
        (first_command, vars), first_psycop_response = history[0]
        value_mapping_as_dict = vars[0]

        self.assertFalse(success)
        self.assertIn('INSERT INTO', first_command)
        self.assertTrue(value_mapping_as_dict.keys())
        self.assertTrue(os.path.exists(spreadsheet_path))  # import file remains but is changed
        self.assertTrue(os.path.exists(success_path))  # successful import copied here for safetyZ


    def test_work_to_do(self):
        self.assertFalse('Line_at_a_time has no problem when the whole file is clean and imports all lines')
        self.assertFalse('test_action cleans up after itself, tests various end cases')








if __name__ == '__main__':
    unittest.main()
