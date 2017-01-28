import os

import file_utilities
import sentry
import cursors
import sql_command_library


def get_current_tableset():
    cmdr = cursors.Commander()
    return cmdr.tableset


def destroy_database_tables(tableset):
    cmdr = cursors.Commander()
    for table in tableset:
        result = cmdr.do_cmd(cmdr.drop_table_string.format(table))
        if result:
            return result
    cmdr.commit()


def make_database_tables(path_to_listings):
    table_builder = sql_command_library.read_db_creation_commands(path_to_listings)
    return issue_database_commands(table_builder)


def make_database_views(path_to_listings):
    view_builder = sql_command_library.read_view_creation_commands(path_to_listings)
    return issue_database_commands(view_builder)


def issue_database_commands(builder):
    psycop_msgs = []
    cmdr = cursors.Commander()
    for name, cmdstring in builder.items():
        psycop_msg = cmdr.do_cmd(cmdstring)
        if psycop_msg:
            psycop_msgs.append(psycop_msg)
    if not psycop_msgs:
        cmdr.commit()
    cmdr.close()
    return psycop_msgs


