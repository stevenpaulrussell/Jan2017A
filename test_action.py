import os
import unittest

import action
import sentry
import setup_common_for_test

import dataqueda_constants
import file_utilities


class CanProperlyHandleWholeTableImports(unittest.TestCase):
    def setUp(self):
        setup_common_for_test.clean_directories()
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

    def test_can_find_and_import_whole_tables(self):
        self.assertEqual(sentry.work_list, [])  # Verify all clear!
        sentry.poll_imports()
        self.assertTrue(len(sentry.work_list) == 1)  # Verify all ok with sentry.  Really, this is not part of action!
        success, history = action.do_a_work_item(connect=dataqueda_constants.LOCAL)
        (cmd, vars), error_msg = history[0]
        self.assertTrue(success)
        self.assertEqual(error_msg, None)
        self.assertEqual(len(vars), 1)
        self.assertIn('last', vars[0])

    def test_import_whole_tables_moves_imported_file_to_archive(self):
        import_file_name = os.path.split(file_utilities.get_path_from_alias('person_table_example'))[-1]
        import_path = file_utilities.get_path_from_alias('import whole person directory')
        archive_path = file_utilities.get_path_from_alias('archive_directory/person')
        before_import, before_archive = next(os.walk(import_path)), next(os.walk(archive_path))
        sentry.poll_imports()
        before_work_list_length = len(sentry.work_list)
        success, history = action.do_a_work_item(connect=dataqueda_constants.LOCAL)
        (cmd, vars), error_msg = history[0]
        after_work_list_length = len(sentry.work_list)
        after_import, after_archive = next(os.walk(import_path)), next(os.walk(archive_path))

        self.assertTrue(success)
        self.assertEqual(error_msg, None)
        self.assertEqual(len(vars), 1)
        self.assertIn('last', vars[0])
        self.assertEqual(before_work_list_length, 1)
        self.assertEqual(after_work_list_length, 0)

        p, d, import_files = before_import
        self.assertIn(import_file_name, import_files)
        p, d, archive_files = before_archive
        self.assertNotIn(import_file_name, archive_files)

        p, d, import_files = after_import
        self.assertNotIn(import_file_name, import_files)
        p, d, archive_files = after_archive
        self.assertIn(import_file_name, archive_files)



    def test_double_import_whole_tables_generates_right_errors(self):
        self.assertEqual(len(sentry.work_list), 0)
        sentry.poll_imports()
        self.assertEqual(len(sentry.work_list), 1)
        action.do_a_work_item(connect=dataqueda_constants.LOCAL)
        self.assertEqual(len(sentry.work_list), 0)

        dest_path = file_utilities.get_path_from_alias('import whole person directory')
        source_path = file_utilities.get_path_from_alias('person_table_example')
        file_utilities.copy_file_path_to_dir(source_path, dest_path)
        sentry.poll_imports()

        dest_path = file_utilities.get_path_from_alias('import whole person directory')
        source_path = file_utilities.get_path_from_alias('person_table_example')
        file_utilities.copy_file_path_to_dir(source_path, dest_path)

        success, history = action.do_a_work_item(connect=dataqueda_constants.LOCAL)
        self.assertTrue(len(sentry.work_list) == 0)  # Work done has cleared the work_list

        (cmd, vars), error_msg = history[0]
        self.assertFalse(success)
        self.assertTrue(len(error_msg) > 20)
        self.assertEqual(len(vars), 1)
        self.assertIn('last', vars[0])
        self.assertIn('IntegrityError', error_msg)

    def test_keywords_source_file_and_author_are_available_for_tables(self):
        self.assertEqual(sentry.work_list, [])  # Verify all clear!
        success, history = action.do_a_work_item(connect=dataqueda_constants.LOCAL)
        (cmd, vars), error_msg = history[0]

        self.assertIn('source_file', vars[0])
        self.assertIn('person', vars[0]['source_file'])
        self.assertIn('author', vars[0])
        self.assertIn('from spreadsheet or cloud AAA', vars[0]['author'])




class CanProperlyHandle_By_Line_TableImportsWithErrorsInImports(unittest.TestCase):
    def setUp(self):
        setup_common_for_test.clean_directories()
        sentry.poll_imports()
        sentry.work_list = []
        dest_path = file_utilities.get_path_from_alias('import lines person directory')
        source_path = file_utilities.get_path_from_alias('person_draft_error')
        file_utilities.copy_file_path_to_dir(source_path, dest_path)

    def tearDown(self):
        sentry.poll_imports()
        sentry.work_list = []
        setup_common_for_test.clean_directories()

    def test_can_find_and_import_tables_by_line(self):
        self.assertEqual(sentry.work_list, [])  # Verify all clear!
        sentry.poll_imports()
        self.assertTrue(len(sentry.work_list) == 1)  # Verify all ok with sentry.  Really, this is not part of action!
        success, history = action.do_a_work_item(connect=dataqueda_constants.LOCAL)
        (cmd, vars), error_msg = history[0]
        self.assertFalse(success)
        self.assertTrue(error_msg)
        self.assertEqual(len(vars), 1)
        self.assertIn('last', vars[0])

    def test_keywords_source_file_and_author_are_available_for_tables(self):
        self.assertEqual(sentry.work_list, [])  # Verify all clear!
        sentry.poll_imports()
        self.assertTrue(len(sentry.work_list) == 1)  # Verify all ok with sentry.  Really, this is not part of action!
        success, history = action.do_a_work_item(connect=dataqueda_constants.LOCAL)
        (cmd, vars), error_msg = history[0]
        self.assertIn('source_file', vars[0])
        self.assertIn('person', vars[0]['source_file'])
        self.assertIn('author', vars[0])
        self.assertIn('from spreadsheet or cloud AAA', vars[0]['author'])


class Test_Actions_Can_Destroy_And_Create_DB(unittest.TestCase):
    def setUp(self):
        setup_common_for_test.clean_directories()
        tableset = action.get_current_tableset(connect=dataqueda_constants.LOCAL)
        if tableset:
            action.destroy_database_tables(tableset, connect=dataqueda_constants.LOCAL)

    def tearDown(self):
        setup_common_for_test.clean_directories()
        tableset = action.get_current_tableset(connect=dataqueda_constants.LOCAL)
        if tableset:
            action.destroy_database_tables(tableset, connect=dataqueda_constants.LOCAL)

    def test_can_make_views(self):
        action.make_database_tables(connect=dataqueda_constants.LOCAL)
        success, history = action.make_database_views(connect=dataqueda_constants.LOCAL)
        (first_command, vars), first_psycop_response = history[0]
        self.assertTrue(success)
        self.assertIn('CREATE VIEW', first_command)
        self.assertEqual(vars, ())
        self.assertFalse(first_psycop_response)

    def test_errors_in_group_commit_detected(self):
        action.make_database_tables(connect=dataqueda_constants.LOCAL)
        success, history = action.make_database_tables(connect=dataqueda_constants.LOCAL)
        (first_command, vars), first_psycop_response = history[0]
        self.assertFalse(success)
        self.assertIn('CREATE TABLE person', first_command)
        self.assertEqual(vars, ())
        self.assertTrue(first_psycop_response)
        self.assertIn('ProgrammingError', first_psycop_response)
        self.assertIn('already exists', first_psycop_response)


class StandaloneTestToDestroyAndMakeDatabaseTables(unittest.TestCase):
    def setUp(self):
        setup_common_for_test.clean_directories()
        tableset = action.get_current_tableset(connect=dataqueda_constants.LOCAL)
        if tableset:
            action.destroy_database_tables(tableset, connect=dataqueda_constants.LOCAL)

    def tearDown(self):
        setup_common_for_test.clean_directories()
        tableset = action.get_current_tableset(connect=dataqueda_constants.LOCAL)
        if tableset:
            action.destroy_database_tables(tableset, connect=dataqueda_constants.LOCAL)

    def test_can_make_tables(self):
        tableset_start = action.get_current_tableset(connect=dataqueda_constants.LOCAL)
        success, history = action.make_database_tables(connect=dataqueda_constants.LOCAL)
        tableset_end = action.get_current_tableset(connect=dataqueda_constants.LOCAL)
        self.assertFalse(tableset_start)
        self.assertTrue(success)
        self.assertIn('person', tableset_end)


if __name__ == '__main__':
    unittest.main()
