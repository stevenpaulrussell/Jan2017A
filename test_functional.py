import unittest
import os

import dataqueda_constants
import file_utilities
import action
import setup_common_for_test

connect = dataqueda_constants.LOCAL
path_to_listings = setup_common_for_test.test_directory
imports_path = path_to_listings['imports_locator']


class RebuildDatabaseFromBaseDocuments(unittest.TestCase):
    def test_can_destroy_and_rebuild_tables(self):
        tables = action.get_current_tableset(connect=connect)
        action.destroy_database_tables(tables, connect=connect)

        successt, historyt = action.make_database_tables(connect=connect)
        successv, historyv = action.make_database_views(connect=connect)
        tables = action.get_current_tableset(connect=connect)
        (first_command, vars), first_psycop_response = historyv[0]

        self.assertTrue(successt)
        self.assertTrue(successv)
        self.assertIn('person', tables)
        self.assertIn('CREATE VIEW', first_command)


class InsertFromImportsSimple(unittest.TestCase):
    def setUp(self):
        setup_common_for_test.clean_directories()
        tables = action.get_current_tableset(connect=connect)
        action.destroy_database_tables(tables, connect=connect)
        action.make_database_tables(connect=connect)
        action.make_database_views(connect=connect)

    def tearDown(self):
        pass
        setup_common_for_test.clean_directories()


    def test_can_import_whole_sheet(self):
        test_file_path = file_utilities.get_path_from_alias('person_table_example')
        test_file_name = os.path.split(test_file_path)[-1]
        destination_directory = file_utilities.get_path_from_alias('import whole person directory')
        imported_file_path  = os.path.join(destination_directory, test_file_name)
        archive_directory = file_utilities.get_path_from_alias('archive_directory/person')
        archive_path = os.path.join(archive_directory, test_file_name)

        file_utilities.copy_file_path_to_dir(test_file_path, destination_directory)

        self.assertTrue(os.path.exists(imported_file_path))
        self.assertFalse(os.path.exists(archive_path))

        success, history = action.do_a_work_item(connect=connect)
        (first_command, vars), first_psycop_response = history[0]
        value_mapping_as_dict = vars[0]

        self.assertTrue(success)
        self.assertIn('INSERT INTO', first_command)
        self.assertTrue(value_mapping_as_dict.keys())
        self.assertFalse(os.path.exists(imported_file_path))
        self.assertTrue(os.path.exists(archive_path))


    def test_failure_import_whole_sheet(self):
        test_file_path = file_utilities.get_path_from_alias('person_table_example')
        test_file_name = os.path.split(test_file_path)[-1]
        destination_directory = file_utilities.get_path_from_alias('import whole person directory')
        imported_file_path  = os.path.join(destination_directory, test_file_name)
        archive_directory = file_utilities.get_path_from_alias('archive_directory/person')
        archive_path = os.path.join(archive_directory, test_file_name)
        fail_file_name = 'ErRoR_{}'.format(test_file_name)
        fail_path = os.path.join(destination_directory, fail_file_name)

        file_utilities.copy_file_path_to_dir(test_file_path, destination_directory)
        self.assertTrue(os.path.exists(imported_file_path))  # import is not removed
        success, history = action.do_a_work_item(connect=connect)
        self.assertFalse(os.path.exists(imported_file_path))  # import is not removed
        self.assertTrue(success)

        should_be_None = action.do_a_work_item(connect=connect)
        self.assertFalse(should_be_None)

        file_utilities.copy_file_path_to_dir(test_file_path, destination_directory)
        success, history = action.do_a_work_item(connect=connect)

        (first_command, vars), first_psycop_response = history[0]
        value_mapping_as_dict = vars[0]
        self.assertFalse(success)
        self.assertIn('duplicate key value violates unique constraint', first_psycop_response)
        self.assertIn('INSERT INTO', first_command)
        self.assertTrue(value_mapping_as_dict.keys())
        self.assertTrue(os.path.exists(imported_file_path))
        self.assertTrue(os.path.exists(fail_path))


class InsertFromImportsIncrementally(unittest.TestCase):
    def setUp(self):
        setup_common_for_test.clean_directories()
        tables = action.get_current_tableset(connect=connect)
        action.destroy_database_tables(tables, connect=connect)
        action.make_database_tables(connect=connect)
        action.make_database_views(connect=connect)

    def tearDown(self):
        setup_common_for_test.clean_directories()

    def test_incremental_with_errors(self):
        test_file_path = file_utilities.get_path_from_alias('person_draft_error')
        test_file_name = os.path.split(test_file_path)[-1]
        destination_directory = file_utilities.get_path_from_alias('import lines person directory')
        imported_file_path  = os.path.join(destination_directory, test_file_name)
        archive_directory = file_utilities.get_path_from_alias('archive_directory/person')
        archive_path = os.path.join(archive_directory, test_file_name)

        file_utilities.copy_file_path_to_dir(test_file_path, destination_directory)
        self.assertTrue(os.path.exists(imported_file_path))  # import file remains but is changed
        success, history = action.do_a_work_item(connect=connect)
        (first_command, vars), first_psycop_response = history[0]
        value_mapping_as_dict = vars[0]

        self.assertFalse(success)
        self.assertIn('INSERT INTO', first_command)
        self.assertTrue(value_mapping_as_dict.keys())
        self.assertIn("""IntegrityError('null value in column "last" violates not-null constraint""",
                      first_psycop_response)
        self.assertTrue(os.path.exists(imported_file_path))  # import file remains but is changed
        self.assertTrue(os.path.exists(archive_path))  # successful import copied here for safetyZ


    def xtest_work_to_do(self):
        self.assertFalse('Line_at_a_time has no problem when the whole file is clean and imports all lines')








if __name__ == '__main__':
    unittest.main()
