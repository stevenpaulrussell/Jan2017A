import os

import file_utilities
import sentry
import cursors
import sql_command_library

BUILD_HISTORY_TABLE = 'build_history'


def do_a_work_item(path_to_listings, connect):
    if not sentry.changed_list:
        return
    change = sentry.changed_list.pop(0)
    insert_cmd = sql_command_library.read_db_insertion_commands(path_to_listings)[change.table_name]
    success, history = general_insert(insert_cmd, change.import_lines, connect=connect, **change.command_keys)
    if success:
        add_to_build_history(change.build_line, path_to_listings=path_to_listings, connect=connect)
        # move from where is to x (routine)
    else:
        pass
        # write failure spreadsheet from history (routine)
        # move or delete from where is (routine)
    return success, history


def insert_whole(insert_cmd, file_path, author, connect):
    return general_insert(insert_cmd, import_lines, connect=connect, **kwds)


def trial_insert_whole():
    pass
    # like insert_whole but no commit.  Re-use with big common, change commit=False, change after-processing



def insert_from_draft():
    pass
    # like insert_whole but single commit, make sure that this will stop processing.  Again, likely use the big
    # common, change commit='single', change post processing


def add_to_build_history(build_line, path_to_listings, connect):
    insert_cmd = sql_command_library.read_db_insertion_commands(path_to_listings)[BUILD_HISTORY_TABLE]
    with cursors.Commander(connect, commit='group') as cmdr:
        cmdr.do_cmd(insert_cmd, build_line)
    print('in action.do_a_work_item.add_to_build_history, need an exception watcher on cmdr.success', cmdr.success)
    print('might be good to move some of this code back to sentry.WorkItem')
    return



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


def general_insert(insert_cmd, import_lines, commit, connect, **kwds):
    with cursors.Commander(connect, commit=commit, **kwds) as cmdr:
        for one_line in import_lines:
            try:
                one_line.update(author=kwds['author'])
                one_line.update(source_file=kwds['source_file'])
            except KeyError:
                pass
            cmdr.do_cmd(insert_cmd, one_line)
    return cmdr.success, cmdr.history


def run_database_commands_as_group(builder, connect, commit):
    with cursors.Commander(connect, commit=commit) as cmdr:
        for cmdstring in builder.values():
            cmdr.do_cmd(cmdstring)
    return cmdr.success, cmdr.history
