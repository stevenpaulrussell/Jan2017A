import os

import file_utilities
import sentry
import cursors
import sql_command_library



def do_a_work_item(connect):
    try:
        work = sentry.work_list.pop(0)
    except IndexError:
        return
    return work


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


