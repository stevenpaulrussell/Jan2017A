import unittest

from file_utilities import spreadsheet_keyvalue_generator

import db_cmd_makers
import db_view_makers
import db_query_makers
import sql_command_library

import setup_common_for_test


test_directory = setup_common_for_test.read_test_locations()


class TestMakingCmdsForTableGenerationFrom_DB_Template(unittest.TestCase):
    def test_can_make_commands_for_generating_table_person(self):
        print('***', test_directory['db_template'])
        template_line_gen = spreadsheet_keyvalue_generator(test_directory['db_template'])
        sql_tables = db_cmd_makers.extract_sql_table_cmds(template_line_gen)
        self.assertIn('person', sql_tables)
        self.assertTrue(len(sql_tables) > 5)
        person_table = sql_tables['person']
        create = 'CREATE TABLE person\n'
        insert1 = 'INSERT INTO person\n'
        insert2 = '\nVALUES\n\t(%(first)s, %(last)s'
        query = 'SELECT first, last'
        self.assertIn(create, person_table.createtable_cmdstring)
        self.assertIn(insert1, person_table.insert_cmdstring)
        self.assertIn(insert2, person_table.insert_cmdstring)
        self.assertIn(query, person_table.create_query_cmd_string)


class TestMakingCmdsForTableGenerationFrom_View_Template(unittest.TestCase):
    def test_can_make_commands_for_view(self):
        template_line_gen = spreadsheet_keyvalue_generator(test_directory['view_template'])
        sql_views = db_view_makers.extract_sql_view_cmds(template_line_gen)
        self.assertIn('tutor_active_view', sql_views)
        self.assertEqual(len(sql_views), 12)
        canada_view = sql_views['canada_view']
        create = 'CREATE VIEW canada_view AS\n\tSELECT moniker,  institution, program, ' \
                 'value, schoolyear, date\n\tFROM program_event\n\tWHERE  ' \
                 'institution  =  (%s)  AND  program  =  (%s)  AND tag = (%s)\n\tvaluelist La Canada, student, Gnumber'
        self.assertEqual(canada_view.create_view_cmd_string, create)


class TestMakingCmdsForTableGenerationFrom_Query_Template(unittest.TestCase):
    def test_can_make_commands_for_query(self):
        template_line_gen = spreadsheet_keyvalue_generator(test_directory['query_template'])
        sql_queries = db_query_makers.extract_sql_query_cmds(template_line_gen)
        self.assertIn('course_completes', sql_queries)
        self.assertEqual(len(sql_queries), 6)
        course_completes = sql_queries['course_completes']
        create = 'SELECT moniker,  schoolyear, schoolterm, classhandle, tag, value\n\tFROM ' \
                 'course_ended_view\n\tWHERE  tag = (%s)\n\tGROUP BY moniker, schoolyear, ' \
                 'schoolterm, classhandle, tag, value\n\tORDER BY moniker, schoolyear, ' \
                 'schoolterm\n\tvaluelist Completed'
        self.assertEqual(course_completes.create_query_cmd_string, create)


class TestRetrievalOfSQLCommandsFromLibrary(unittest.TestCase):
    def test_can_retrieve_table_create_commands(self):
        sql_command_library.write_db_creation_commands(test_directory)
        sql_command_library.write_view_creation_commands(test_directory)
        sql_command_library.write_query_creation_commands(test_directory)
        db_creation_commands = sql_command_library.read_db_creation_commands(test_directory)
        view_creation_commands = sql_command_library.read_view_creation_commands(test_directory)
        query_creation_commands = sql_command_library.read_query_creation_commands(test_directory)
        self.assertIn('person', db_creation_commands)
        self.assertIn('aka_vitals_view', view_creation_commands)
        self.assertIn('scholarships_per_schoolyear', query_creation_commands)


if __name__ == '__main__':
    unittest.main()
