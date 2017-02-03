import os
import shutil
import unittest

import action
import file_utilities
import sentry
import setup_common_for_test

import dataqueda_constants
import filemoves

test_directory = setup_common_for_test.read_test_locations()
imports_path = test_directory['imports_locator']


class CanProperlyHandleWholeTableImports(unittest.TestCase):
    def setUp(self):
        self.file_to_get = set()
        sentry.poll_imports(imports_path)
        sentry.changed_list = []
        to_match = dict(table='person', action='import whole', system='steve air')
        path = filemoves.find_unique_import_directory_matching_pattern(imports_path, **to_match)
        to_get = filemoves.copy_alias_to_path('person_table_example', test_directory, path)
        self.file_to_get.add(to_get)

    def tearDown(self):
        for a_file_path in self.file_to_get:
            os.remove(a_file_path)
        sentry.poll_imports(imports_path)
        sentry.changed_list = []

    def test_can_find_and_import_whole_tables(self):
        self.assertEqual(sentry.changed_list, [])  # Verify all clear!
        sentry.poll_imports(imports_path)
        self.assertTrue(len(sentry.changed_list) == 1)  # Verify all ok with sentry.  Really, this is not part of action!
        success, history = action.do_a_work_item(test_directory, connect=dataqueda_constants.LOCAL)
        (cmd, vars), error_msg = history[0]
        self.assertTrue(success)
        self.assertEqual(error_msg, None)
        self.assertEqual(len(vars), 1)
        self.assertIn('last', vars[0])

    def test_double_import_whole_tables_generates_right_errors(self):
        self.assertEqual(sentry.changed_list, [])  # Verify all clear!
        sentry.poll_imports(imports_path)
        self.assertTrue(len(sentry.changed_list) == 1)  # Verify all ok with sentry.  Really, this is not part of action!
        success, history = action.do_a_work_item(test_directory, connect=dataqueda_constants.LOCAL)
        self.assertTrue(len(sentry.changed_list) == 0)  # Work done has cleared the work_list
        self.tearDown()                         # Remove import file, sentry sees, clear that seeing away
        # redo the import !
        to_match = dict(table='person', action='import whole', system='steve air')
        path = filemoves.find_unique_import_directory_matching_pattern(imports_path, **to_match)
        to_get = filemoves.copy_alias_to_path('person_table_example', test_directory, path)
        self.file_to_get.add(to_get)

        sentry.poll_imports(imports_path)
        self.assertTrue(len(sentry.changed_list) == 1)  # Verify all ok with sentry.  Really, this is not part of action!
        success, history = action.do_a_work_item(test_directory, connect=dataqueda_constants.LOCAL)
        self.assertTrue(len(sentry.changed_list) == 0)  # Work done has cleared the work_list

        (cmd, vars), error_msg = history[0]
        self.assertFalse(success)
        self.assertTrue(len(error_msg) > 20)
        self.assertEqual(len(vars), 1)
        self.assertIn('last', vars[0])
        self.assertIn('IntegrityError', error_msg)

    def test_keywords_source_file_and_author_are_available_for_tables(self):
        self.assertEqual(sentry.changed_list, [])  # Verify all clear!
        sentry.poll_imports(imports_path)
        self.assertTrue(len(sentry.changed_list) == 1)  # Verify all ok with sentry.  Really, this is not part of action!
        success, history = action.do_a_work_item(test_directory, connect=dataqueda_constants.LOCAL)
        (cmd, vars), error_msg = history[0]
        import_file_path = self.file_to_get.copy().pop()
        import_file_name = os.path.split(import_file_path)[-1]
        self.assertIn('source_file', vars[0])
        self.assertEqual(import_file_name, vars[0]['source_file'])
        self.assertIn('author', vars[0])
        self.assertIn('from imports_locator spreadsheet or cloud services', vars[0]['author'])




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
