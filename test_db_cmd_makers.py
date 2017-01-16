import unittest

from file_utilities import spreadsheet_keyvalue_generator
from test_severalitems import test_db_template_path
from test_severalitems import test_view_template_path
from test_severalitems import test_query_template_path

import db_cmd_makers
import db_view_makers
import db_query_makers
import sql_command_library


class TestMakingCmdsForTableGenerationFrom_DB_Template(unittest.TestCase):
    def test_can_make_commands_for_generating_table_person(self):
        template_line_gen = spreadsheet_keyvalue_generator(test_db_template_path)
        sql_tables = db_cmd_makers.extract_sql_table_cmds(template_line_gen)
        self.assertIn('person', sql_tables)
        self.assertEqual(len(sql_tables), 12)
        person_table = sql_tables['person']
        create = 'CREATE TABLE person\n\t(\n\tfirst VARCHAR(80) ' \
                   'NOT NULL,\n\tlast VARCHAR(80) NOT NULL,\n\tbirth DATE NOT NULL,\n\tsex VARCHAR(80),' \
                   '\n\tjoined_year INT NOT NULL,\n\tjoined_term VARCHAR(80) NOT NULL,\n\tsource VARCHAR(80),' \
                   '\n\tCONSTRAINT personPK PRIMARY KEY (first, last, birth)\n\t)'

        insert = 'INSERT INTO person\n\t(first, last, birth, sex, joined_year, ' \
                 'joined_term, source)\nVALUES\n\t(%(first)s, %(last)s, %(birth)s, %(sex)s,' \
                 ' %(joined_year)s, %(joined_term)s, %(source)s)'

        query = 'SELECT first, last, birth, sex, joined_year, joined_term, source\n\tFROM person'

        self.assertEqual(person_table.createtable_cmdstring, create)
        self.assertEqual(person_table.insert_cmdstring, insert)
        self.assertEqual(person_table.create_query_cmd_string, query)


class TestMakingCmdsForTableGenerationFrom_View_Template(unittest.TestCase):
    def test_can_make_commands_for_view(self):
        template_line_gen = spreadsheet_keyvalue_generator(test_view_template_path)
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
        template_line_gen = spreadsheet_keyvalue_generator(test_query_template_path)
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
        print(1, sql_command_library.read_db_creation_commands())
        sql_command_library.write_db_creation_commands()
        print(2, sql_command_library.read_db_creation_commands())


if __name__ == '__main__':
    unittest.main()
