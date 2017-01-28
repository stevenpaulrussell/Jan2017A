import os

import file_utilities
import sentry
import cursors
import sql_command_library






def get_current_tableset(**kwds):
    return cursors.Commander(**kwds).tableset


def destroy_database_tables(tableset, connect):
    with cursors.Commander(connect) as cmdr:
        for table in tableset:
            result = cmdr.do_cmd(cmdr.drop_table_string.format(table))
            if result:
                return result
        cmdr.commit()


def make_database_tables(path_to_listings, connect):
    table_builder = sql_command_library.read_db_creation_commands(path_to_listings)
    return run_database_commands_as_group(table_builder, connect)


def make_database_views(path_to_listings, connect):
    view_builder = sql_command_library.read_view_creation_commands(path_to_listings)
    return run_database_commands_as_group(view_builder, connect)


def run_database_commands_as_group(builder, connect):
    psycop_msgs = []
    with cursors.Commander(connect) as cmdr:
        for name, cmdstring in builder.items():
            psycop_msgs.append(cmdr.do_cmd(cmdstring))
        if any(psycop_msgs):
            return psycop_msgs
        else:
            cmdr.commit()


