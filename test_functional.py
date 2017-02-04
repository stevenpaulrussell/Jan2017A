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
print('imports_path', imports_path)


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
        imports_gen = file_utilities.spreadsheet_keyvalue_generator(imports_path)
        for location in imports_gen:
            directory_path = location['path']
            this_path, dirs, files = os.walk(directory_path).__next__()
            for filename in files:
                filepath = os.path.join(this_path, filename)
                os.remove(filepath)
        tables = action.get_current_tableset(connect=connect)
        action.destroy_database_tables(tables, connect=connect)
        action.make_database_tables(path_to_listings=path_to_listings, connect=connect)
        action.make_database_views(path_to_listings, connect=connect)

    def tearDown(self):
        imports_gen = file_utilities.spreadsheet_keyvalue_generator(imports_path)
        for location in imports_gen:
            directory_path = location['path']
            this_path, dirs, files = os.walk(directory_path).__next__()
            for filename in files:
                filepath = os.path.join(this_path, filename)
                os.remove(filepath)

    def test_can_import_whole_sheet(self):
        to_match = dict(table='person', action='import whole', system='steve air')
        import_copy_to_path = filemoves.find_unique_import_directory_matching_pattern(imports_path, **to_match)
        test_spreadsheet_path = filemoves.copy_alias_to_path('person_table_example', path_to_listings,
                                                             import_copy_to_path)

        success, history = action.do_a_work_item(path_to_listings, connect=connect)
        (first_command, vars), first_psycop_response = history[0]
        value_mapping_as_dict = vars[0]

        self.assertTrue(success)
        self.assertIn('INSERT INTO', first_command)
        self.assertTrue(value_mapping_as_dict.keys())
        self.assertFalse(os.path.exists(test_spreadsheet_path))  # import should have been removed
        self.assertTrue(os.path.exists('Successful import path'))  # successful import copied here for safety
        self.assertFalse(os.path.exists('Error path'))  # unsuccessful import copied here for work



if __name__ == '__main__':
    unittest.main()
