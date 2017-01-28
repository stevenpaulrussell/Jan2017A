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
    cmdr = cursors.Commander()
    table_builder = sql_command_library.read_db_creation_commands(path_to_listings)
    for name, create_table_cmdstring in table_builder.items():
        print('\ntable "{}"\n"{}"\n'.format(name, create_table_cmdstring))
        result = cmdr.do_cmd(create_table_cmdstring)
        print('sql result "{}"\n'.format(result))
    cmdr.commit()
    cmdr.close()


def make_database_views(path_to_listings):
    cmdr = cursors.Commander()
    view_builder = sql_command_library.read_view_creation_commands(path_to_listings)
    for name, create_view_cmdstring in view_builder.items():
        result = cmdr.do_cmd(create_view_cmdstring)
        if result:
            print('error in make_database_views', result)
        else:
            cmdr.commit()
    cmdr.close()



