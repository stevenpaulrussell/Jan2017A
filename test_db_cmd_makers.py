import unittest

from file_utilities import spreadsheet_keyvalue_generator
from test_severalitems import test_db_template_path

import db_cmd_makers


class TestMakingCmdsForTableGenerationFrom_DB_Template(unittest.TestCase):
    def test_can_make_commands_for_person_table(self):
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

        print(person_table.createtable_cmdstring)
        print()
        print(person_table.insert_cmdstring)
        print()
        print(person_table.create_query_cmd_string)



if __name__ == '__main__':
    unittest.main()
