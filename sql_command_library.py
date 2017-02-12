import collections
import os

import file_utilities
import db_cmd_makers, db_view_makers, db_query_makers


def read_db_creation_commands():
    return file_utilities.read_cmds_as_list('create_table_cmds')


def read_db_insertion_commands():
    return file_utilities.read_cmds_as_list('insert_into_table_cmds')


def read_view_creation_commands():
    return file_utilities.read_cmds_as_list('create_view_cmds')


def read_query_creation_commands():
    query_command_list = collections.OrderedDict()
    for query_file in ('table_as_query_cmds', 'view_as_query_cmds', 'create_query_cmds'):
        query_command_list.update(file_utilities.read_cmds_as_list(query_file))
    return query_command_list


def write_db_creation_commands():
    template_line_gen = file_utilities.key_values_from_alias('db_template')
    db_commands = db_cmd_makers.extract_sql_table_cmds(template_line_gen)
    create_path = clean_and_return_path('create_table_cmds')
    insert_path = clean_and_return_path('insert_into_table_cmds')
    query_path = clean_and_return_path('table_as_query_cmds')
    for table_name, table in db_commands.items():
        write_cmd_string(table_name, create_path, table.createtable_cmdstring)
        write_cmd_string(table_name, insert_path, table.insert_cmdstring)
        write_cmd_string(table_name, query_path, table.create_query_cmd_string)


def write_view_creation_commands():
    template_line_gen = file_utilities.key_values_from_alias('view_template')
    view_commands = db_view_makers.extract_sql_view_cmds(template_line_gen)
    create_path = clean_and_return_path('create_view_cmds')
    query_path = clean_and_return_path('view_as_query_cmds')
    for view_name, view in view_commands.items():
        write_cmd_string(view_name, create_path, view.create_view_cmd_string)
        write_cmd_string(view_name, query_path, view.create_query_cmd_string)


def write_query_creation_commands():
    template_line_gen = file_utilities.key_values_from_alias('query_template')
    query_commands = db_query_makers.extract_sql_query_cmds(template_line_gen)
    query_path = clean_and_return_path('create_query_cmds')
    for query_name, query in query_commands.items():
        write_cmd_string(query_name, query_path, query.create_query_cmd_string)


def write_cmd_string(item_name, my_path, command_string):
    with open(my_path, 'a') as fp:
        fp.write('{}\n{}\n\n'.format(item_name, command_string))


def clean_and_return_path(alias):
    my_path = file_utilities.get_path_from_alias(alias)
    if os.path.exists(my_path):
        os.remove(my_path)
    return my_path