import collections
import yaml

import file_utilities

import db_cmd_makers, db_view_makers, db_query_makers



def read_db_creation_commands(my_directory):
    db_creation_commands = collections.OrderedDict()
    with open(my_directory['create_table_cmds'], 'r') as fp:
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
    write_cmds(my_directory['create_table_cmds'], [table.createtable_cmdstring for table in db_commands.values()])
    write_cmds(my_directory['insert_into_table_cmds'], [table.insert_cmdstring for table in db_commands.values()])
    write_cmds(my_directory['table_as_query_cmds'], [table.create_query_cmd_string for table in db_commands.values()])


def write_view_creation_commands(my_directory):
    template_line_gen = file_utilities.spreadsheet_keyvalue_generator(my_directory['view_template'])
    view_commands = db_view_makers.extract_sql_view_cmds(template_line_gen)
    write_cmds(my_directory['create_view_cmds'], [view.create_view_cmd_string for view in view_commands.values()])
    write_cmds(my_directory['view_as_query_cmds'], [view.create_query_cmd_string for view in view_commands.values()])


def write_query_creation_commands(my_directory):
    template_line_gen = file_utilities.spreadsheet_keyvalue_generator(my_directory['query_template'])
    query_commands = db_query_makers.extract_sql_query_cmds(template_line_gen)
    write_cmds(my_directory['create_query_cmds'], [query.create_query_cmd_string for query in query_commands.values()])


def write_cmds(my_path, my_gen):
    with open(my_path, 'w') as fp:
        for item in my_gen:
            fp.write(item + '\n\n')

