import collections
import yaml

import file_utilities

import db_cmd_makers, db_view_makers, db_query_makers



def read_db_creation_commands(my_directory):
    db_creation_commands = collections.OrderedDict()
    with open(my_directory['sql_create_tables'], 'r') as fp:
        commands_as_string = fp.read()
    commands_as_list = commands_as_string.split('\n\n')
    for item in commands_as_list:
        firstline = item.split('\n')[0]
        tablename = firstline.split(' TABLE ')[-1].strip()
        db_creation_commands[tablename] = item
    return db_creation_commands


def write_db_creation_commands(my_directory):
    template_line_gen = file_utilities.spreadsheet_keyvalue_generator(my_directory['db_template'])
    db_commands = db_cmd_makers.extract_sql_table_cmds(template_line_gen)
    create_tables = [table.createtable_cmdstring for table in db_commands.values()]
    with open(my_directory['sql_create_tables'], 'w') as fp:
        for item in create_tables:
            fp.write(item + '\n\n')

