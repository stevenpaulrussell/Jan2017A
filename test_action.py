import os
import shutil
import unittest

import action
import file_utilities
import sentry
import setup_common_for_test

import dataqueda_constants

test_directory = setup_common_for_test.read_test_locations()
imports_path = test_directory['imports_locator']


class CanProperlyHandleVariousImports(unittest.TestCase):
    def setUp(self):
        person_table_path = test_directory['person_table_example']
        person_file_name = os.path.split(person_table_path)[-1]
        imports_gen = file_utilities.spreadsheet_keyvalue_generator(imports_path)
        for location in imports_gen:
            if location['table'] == 'person' and location['action'] == 'import whole':
                path_to_import_folder = location['path']
        self.path_to_person_file_in_import_folder = os.path.join(path_to_import_folder, person_file_name)
        if os.path.exists(self.path_to_person_file_in_import_folder):
            print('occupied')
            os.remove(self.path_to_person_file_in_import_folder)
        sentry.poll_imports(imports_path)
        sentry.work_list = []
        shutil.copyfile(person_table_path, self.path_to_person_file_in_import_folder)

    def tearDown(self):
        if os.path.exists(self.path_to_person_file_in_import_folder):
            os.remove(self.path_to_person_file_in_import_folder)
        sentry.poll_imports(imports_path)
        sentry.work_list = []

    def test_can_find_and_import_whole_tables(self):
        self.assertEqual(sentry.work_list, [])  # Verify all clear!
        self.assertTrue(os.path.exists(self.path_to_person_file_in_import_folder))  # Verify have file copied
        sentry.poll_imports(imports_path)
        self.assertTrue(len(sentry.work_list) == 1)  # Verify all ok with sentry.  Really, this is not part of action!
        work = action.do_a_work_item(connect=dataqueda_constants.LOCAL)
        if work:
            print(work.table_name)
            print(work.to_do)
            print(work.__dict__)


class Test_Actions_Can_Destroy_And_Create_DB(unittest.TestCase):
    def setUp(self):
        self.tableset = action.get_current_tableset(connect=dataqueda_constants.LOCAL)

    def test_can_retrieve_tables(self):
        if self.tableset:
            self.assertIn('person', self.tableset)
        else:
            print('No tables seen in test_action.Test_Actions_Can_Destroy_And_Create_DB.test_can_retrieve_tables')

    def test_destroy_database_tables(self):
        if self.tableset:
            success, history = action.destroy_database_tables(self.tableset, connect=dataqueda_constants.LOCAL)
            self.assertTrue(success)
            (first_command, vars), first_psycop_response = history[0]
            self.assertIn('DROP TABLE IF EXISTS', first_command)
            self.assertEqual(vars, ())
            self.assertFalse(first_psycop_response)
        else:
            print('No tables to destroy in '
                  'test_action.Test_Actions_Can_Destroy_And_Create_DB.test_destroy_database_tables')

    def test_can_make_views(self):
        success, history = action.make_database_views(test_directory, connect=dataqueda_constants.LOCAL)
        (first_command, vars), first_psycop_response = history[0]
        self.assertTrue(success)
        self.assertIn('CREATE VIEW', first_command)
        self.assertEqual(vars, ())
        self.assertFalse(first_psycop_response)

    def test_errors_in_group_commit_detected(self):
        if self.tableset:
            action.destroy_database_tables(self.tableset, connect=dataqueda_constants.LOCAL)
        action.make_database_tables(test_directory, connect=dataqueda_constants.LOCAL)
        success, history = action.make_database_tables(test_directory, connect=dataqueda_constants.LOCAL)
        (first_command, vars), first_psycop_response = history[0]
        self.assertFalse(success)
        self.assertIn('CREATE TABLE person', first_command)
        self.assertEqual(vars, ())
        self.assertTrue(first_psycop_response)
        self.assertIn('ProgrammingError', first_psycop_response)
        self.assertIn('already exists', first_psycop_response)


if __name__ == '__main__':
    unittest.main()
