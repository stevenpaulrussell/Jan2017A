import collections
import os
import yaml

import file_utilities

import db_cmd_makers, db_view_makers, db_query_makers


def read_db_creation_commands(my_directory):
    return read_cmds_as_list(my_directory['create_table_cmds'])


def read_view_creation_commands(my_directory):
    return read_cmds_as_list(my_directory['create_view_cmds'])


def read_query_creation_commands(my_directory):
    return read_cmds_as_list(my_directory['create_query_cmds'])


def read_cmds_as_list(my_path):
    wanted = collections.OrderedDict()
    with open(my_path, 'r') as fp:
        commands_as_string = fp.read().strip()
    commands_as_list = commands_as_string.split('\n\n')
    for item in commands_as_list:
        lines = item.split('\n')
        item_name, item = lines[0], '\n'.join(lines[1:])
        wanted[item_name] = item
    return wanted


def write_db_creation_commands(my_directory):
    template_line_gen = file_utilities.spreadsheet_keyvalue_generator(my_directory['db_template'])
    db_commands = db_cmd_makers.extract_sql_table_cmds(template_line_gen)
    create_path = clean_and_return_path(my_directory, 'create_table_cmds')
    insert_path = clean_and_return_path(my_directory, 'insert_into_table_cmds')
    query_path = clean_and_return_path(my_directory, 'table_as_query_cmds')
    for table_name, table in db_commands.items():
        write_cmd_string(table_name, create_path, table.createtable_cmdstring)
        write_cmd_string(table_name, insert_path, table.insert_cmdstring)
        write_cmd_string(table_name, query_path, table.create_query_cmd_string)


def write_view_creation_commands(my_directory):
    template_line_gen = file_utilities.spreadsheet_keyvalue_generator(my_directory['view_template'])
    view_commands = db_view_makers.extract_sql_view_cmds(template_line_gen)
    create_path = clean_and_return_path(my_directory, 'create_view_cmds')
    query_path = clean_and_return_path(my_directory, 'view_as_query_cmds')
    for view_name, view in view_commands.items():
        write_cmd_string(view_name, create_path, view.create_view_cmd_string)
        write_cmd_string(view_name, query_path, view.create_query_cmd_string)


def write_query_creation_commands(my_directory):
    template_line_gen = file_utilities.spreadsheet_keyvalue_generator(my_directory['query_template'])
    query_commands = db_query_makers.extract_sql_query_cmds(template_line_gen)
    query_path = clean_and_return_path(my_directory, 'create_query_cmds')
    for query_name, query in query_commands.items():
        write_cmd_string(query_name, query_path, query.create_query_cmd_string)


def write_cmd_string(item_name, my_path, command_string):
    with open(my_path, 'a') as fp:
        fp.write('{}\n{}\n\n'.format(item_name, command_string))

def clean_and_return_path(my_directory, alias):
    my_path = my_directory[alias]
    if os.path.exists(my_path):
        os.remove(my_path)
    return my_path