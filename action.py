import os

import file_utilities
import sentry
import cursors
import sql_command_library


def do_a_work_item(path_to_listings, connect):
    try:
        work = sentry.work_list.pop(0)
    except IndexError:
        return
    if (work.to_do, work.file_change) in [('import whole','new'),]:
        return insert_whole(work.table_name, work.file_path, path_to_listings, connect)
    else:
        print('In action, do not know what to do with work item "{}"'.format(work.__dict__))


def insert_whole(table_name, file_path, path_to_listings, connect):
    all_table_insert_commands = sql_command_library.read_db_insertion_commands(path_to_listings)
    one_cmd = all_table_insert_commands[table_name]
    new_lines = file_utilities.spreadsheet_keyvalue_generator(file_path)
    with cursors.Commander(connect, commit='group') as cmdr:
        for one_line in new_lines:
            cmdr.do_cmd(one_cmd, one_line)
    return cmdr.success, cmdr.history


def get_current_tableset(connect):
    return cursors.Commander(connect=connect).tableset


def destroy_database_tables(tableset, connect):
    with cursors.Commander(connect, commit='group') as cmdr:
        for table in tableset:
            cmdr.do_cmd(cmdr.drop_table_string.format(table))
    return cmdr.success, cmdr.history


def make_database_tables(path_to_listings, connect):
    table_builder = sql_command_library.read_db_creation_commands(path_to_listings)
    success, history = run_database_commands_as_group(table_builder, connect, commit='group')
    return success, history


def make_database_views(path_to_listings, connect):
    view_builder = sql_command_library.read_view_creation_commands(path_to_listings)
    success, history = run_database_commands_as_group(view_builder, connect, commit='group')
    return success, history


def run_database_commands_as_group(builder, connect, commit):
    with cursors.Commander(connect, commit=commit) as cmdr:
        for name, cmdstring in builder.items():
            cmdr.do_cmd(cmdstring)
    return cmdr.success, cmdr.history
