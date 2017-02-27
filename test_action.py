import os
import unittest

import action
import sentry
import setup_common_for_test
import cursors

import dataqueda_constants
import file_utilities
from dataqueda_constants import LOCAL


class CanTestImports(unittest.TestCase):
    def setUp(self):
        setup_common_for_test.clean_directories()
        tableset = action.get_current_tableset(connect=LOCAL)
        action.destroy_database_tables(tableset, connect=LOCAL)
        action.make_database_tables(connect=dataqueda_constants.LOCAL)
        action.make_database_views(connect=dataqueda_constants.LOCAL)
        sentry.poll_imports()
        sentry.work_list = []

    def tearDown(self):
        sentry.poll_imports()
        sentry.work_list = []
        tableset = action.get_current_tableset(connect=dataqueda_constants.LOCAL)
        if tableset:
            action.destroy_database_tables(tableset, connect=dataqueda_constants.LOCAL)
        setup_common_for_test.clean_directories()

    def test_import_test_only_spreadsheet_fails_to_import_even_if_could(self):
        destination_directory = file_utilities.get_path_from_alias('import person test directory')
        test_path = file_utilities.get_path_from_alias('person_table_example')
        test_file_name = os.path.split(test_path)[-1]
        success_file_name = 'SuCcEsS_{}'.format(test_file_name)
        file_utilities.copy_file_path_to_dir(test_path, destination_directory)
        success, history = action.do_a_work_item(connect=dataqueda_constants.LOCAL)
        (cmd, vars), error_msg = history[0]
        p, d, files = next(os.walk(destination_directory))

        self.assertTrue(success)
        self.assertFalse(error_msg)
        self.assertIn(test_file_name, files)
        self.assertIn(success_file_name, files)

        with cursors.Commander(connect=LOCAL) as cmdr:
            cmdr.do_query('SELECT first, last, key_date FROM person')
        success, history, report = cmdr.success, cmdr.history, [item for item in cmdr.query_response_gen]

        self.assertEqual(len(report), 1)
        self.assertDictEqual(report[0], {'first': ' ', 'last': ' ', 'key_date FROM person': ' '})


    def test_import_test_only_spreadsheet_fails_properly(self):
        destination_directory = file_utilities.get_path_from_alias('import person test directory')
        test_path = file_utilities.get_path_from_alias('person_draft_error')
        test_file_name = os.path.split(test_path)[-1]
        fail_file_name = 'ErRoR_{}'.format(test_file_name)

        file_utilities.copy_file_path_to_dir(test_path, destination_directory)
        success, history = action.do_a_work_item(connect=dataqueda_constants.LOCAL)
        error_msg = [e for (a, e) in history if e][0]
        p, d, files = next(os.walk(destination_directory))

        self.assertFalse(success)
        self.assertIn('IntegrityError', error_msg)
        self.assertIn(test_file_name, files)
        self.assertIn(fail_file_name, files)


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

    def test_can_find_and_import_whole_tables(self):
        self.assertEqual(len(sentry.work_list), 0)      # File added in setUp not yet noticed
        sentry.poll_imports()
        self.assertTrue(len(sentry.work_list) == 1)
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
        action.do_a_work_item(connect=dataqueda_constants.LOCAL)
        after_import, after_archive = next(os.walk(import_path)), next(os.walk(archive_path))

        p, d, import_files = before_import
        self.assertIn(import_file_name, import_files)
        p, d, archive_files = before_archive
        self.assertNotIn(import_file_name, archive_files)

        p, d, import_files = after_import
        self.assertNotIn(import_file_name, import_files)
        p, d, archive_files = after_archive
        self.assertIn(import_file_name, archive_files)


    def test_double_import_whole_tables_generates_right_errors(self):
        action.do_a_work_item(connect=dataqueda_constants.LOCAL)
        dest_path = file_utilities.get_path_from_alias('import whole person directory')
        source_path = file_utilities.get_path_from_alias('person_table_example')

        file_utilities.copy_file_path_to_dir(source_path, dest_path)
        success, history = action.do_a_work_item(connect=dataqueda_constants.LOCAL)
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
        self.assertIn('steve', vars[0]['author'])


class CanProperlyHandle_By_Line_TableImportsWithErrorsInImports(unittest.TestCase):
    def setUp(self):
        setup_common_for_test.clean_directories()
        tableset = action.get_current_tableset(connect=LOCAL)
        action.destroy_database_tables(tableset, connect=LOCAL)
        action.make_database_tables(connect=dataqueda_constants.LOCAL)
        action.make_database_views(connect=dataqueda_constants.LOCAL)
        sentry.poll_imports()
        sentry.work_list = []
        self.dest_dir = file_utilities.get_path_from_alias('import lines person directory')

    def tearDown(self):
        sentry.poll_imports()
        sentry.work_list = []
        setup_common_for_test.clean_directories()

    def test_can_find_and_import_tables_by_line(self):
        source_path = file_utilities.get_path_from_alias('person_draft_error')
        source_name = os.path.split(source_path)[-1]
        dest_path = os.path.join(self.dest_dir, source_name)
        file_utilities.copy_file_path_to_dir(source_path, self.dest_dir)
        import_path = os.path.join(self.dest_dir, )
        self.assertEqual(sentry.work_list, [])  # Verify all clear!
        sentry.poll_imports()
        self.assertTrue(len(sentry.work_list) == 1)  # Verify all ok with sentry.  Really, this is not part of action!
        success, history = action.do_a_work_item(connect=dataqueda_constants.LOCAL)
        (cmd, vars), error_msg = history[0]
        self.assertFalse(success)
        self.assertTrue(error_msg)
        self.assertEqual(len(vars), 1)
        self.assertIn('last', vars[0])
        self.assertTrue(os.path.exists(dest_path))

        self.assertEqual(sentry.work_list, [])  # Verify all clear after work done!
        sentry.poll_imports()
        self.assertTrue(len(sentry.work_list) == 0)  # Verify no more to be done!


    def test_keywords_source_file_and_author_are_available_for_tables(self):
        source_path = file_utilities.get_path_from_alias('person_draft_error')
        file_utilities.copy_file_path_to_dir(source_path, self.dest_dir)
        self.assertEqual(sentry.work_list, [])  # Verify all clear!
        sentry.poll_imports()
        self.assertTrue(len(sentry.work_list) == 1)  # Verify all ok with sentry.  Really, this is not part of action!
        success, history = action.do_a_work_item(connect=dataqueda_constants.LOCAL)
        (cmd, vars), error_msg = history[0]
        self.assertIn('source_file', vars[0])
        self.assertIn('person', vars[0]['source_file'])
        self.assertIn('author', vars[0])
        self.assertIn('tania', vars[0]['author'])

    def test_does_xls_to_xlsx_translation(self):
        source_path = file_utilities.get_path_from_alias('person_xls')
        dest_path = os.path.join(self.dest_dir, os.path.split(source_path)[-1])
        re_written_path = '{}.xlsx'.format(os.path.splitext(dest_path)[0])
        print(re_written_path)
        file_utilities.copy_file_path_to_dir(source_path, self.dest_dir)
        self.assertEqual(sentry.work_list, [])  # Verify all clear!
        sentry.poll_imports()
        self.assertTrue(len(sentry.work_list) == 1)  # Verify all ok with sentry.  Really, this is not part of action!
        success, history = action.do_a_work_item(connect=dataqueda_constants.LOCAL)
        (cmd, vars), error_msg = history[0]
        self.assertTrue(success)
        self.assertFalse(error_msg)
        self.assertEqual(len(vars), 1)
        self.assertIn('last', vars[0])
        self.assertFalse(os.path.exists(dest_path))
        self.assertTrue(os.path.exists(re_written_path))
        transformed_import_file = [line for line in file_utilities.spreadsheet_keyvalue_generator(re_written_path)]
        self.assertEqual(len(transformed_import_file), 1)
        self.assertFalse(any(transformed_import_file[0].values()))

        return

        self.assertEqual(sentry.work_list, [])  # Verify all clear!
        sentry.poll_imports()
        self.assertTrue(len(sentry.work_list) == 1)  # Verify all ok with sentry.  Really, this is not part of action!
        success, history = action.do_a_work_item(connect=dataqueda_constants.LOCAL)
        (cmd, vars), error_msg = history[0]
        self.assertTrue(success)
        self.assertFalse(error_msg)
        self.assertEqual(len(vars), 1)
        self.assertIn('last', vars[0])

    def test_handles_empty_imports(self):
        source_path = file_utilities.get_path_from_alias('person_blank')
        source_name = os.path.split(source_path)[-1]
        dest_path = os.path.join(self.dest_dir, source_name)
        file_utilities.copy_file_path_to_dir(source_path, self.dest_dir)
        import_path = os.path.join(self.dest_dir, )
        self.assertEqual(sentry.work_list, [])  # Verify all clear!
        sentry.poll_imports()
        self.assertTrue(len(sentry.work_list) == 1)  # Verify all ok with sentry.  Really, this is not part of action!
        success, history = action.do_a_work_item(connect=dataqueda_constants.LOCAL)
        (cmd, vars), error_msg = history[0]
        self.assertFalse(success)
        self.assertTrue(error_msg)
        self.assertEqual(len(vars), 1)
        self.assertIn('last', vars[0])
        self.assertTrue(os.path.exists(dest_path))

        self.assertEqual(sentry.work_list, [])  # Verify all clear after work done!
        sentry.poll_imports()
        self.assertTrue(len(sentry.work_list) == 0)  # Verify no more to be done!






    def test_handles_perfect_imports_ok(self):
        source_path = file_utilities.get_path_from_alias('person_table_example')
        dest_path = os.path.join(self.dest_dir, os.path.split(source_path)[-1])
        file_utilities.copy_file_path_to_dir(source_path, self.dest_dir)
        self.assertEqual(sentry.work_list, [])  # Verify all clear!
        sentry.poll_imports()
        self.assertTrue(len(sentry.work_list) == 1)  # Verify all ok with sentry.  Really, this is not part of action!
        success, history = action.do_a_work_item(connect=dataqueda_constants.LOCAL)
        (cmd, vars), error_msg = history[0]
        self.assertTrue(success)
        self.assertFalse(error_msg)
        self.assertEqual(len(vars), 1)
        self.assertIn('last', vars[0])
        self.assertTrue(os.path.exists(dest_path))
        transformed_import_file = [line for line in file_utilities.spreadsheet_keyvalue_generator(dest_path)]
        self.assertEqual(len(transformed_import_file), 1)
        self.assertFalse(any(transformed_import_file[0].values()))

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
