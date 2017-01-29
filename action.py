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
    if work.file_change == 'missing':
        return False, work
    else:
        table_name, to_do, file_path, path_to_listings = work.table_name, work.to_do, work.file_path, path_to_listings
        all_table_insert_commands = sql_command_library.read_db_insertion_commands(path_to_listings)
        insert_cmd = all_table_insert_commands[table_name]
        import_lines = file_utilities.spreadsheet_keyvalue_generator(file_path)
    if (to_do, work.file_change) in [('import whole','new'),]:
        return insert_whole(insert_cmd, import_lines, connect)
    else:
        print('In do_a_work_item, do not know what to do with work item "{}"'.format(work.__dict__))


def insert_whole(insert_cmd, import_lines, connect):
    success, history = general_insert(insert_cmd, import_lines, 'group', connect)
    if success:
        pass
        # add to build history (routine)
        # move from where is to x (routine)
    else:
        print('insert_whole saw failure')
        # write failure spreadsheet from history (routine)
        # move or delete from where is (routine)
    return success, history



def trial_insert_whole():
    pass
    # like insert_whole but no commit.  Re-use with big common, change commit=False, change after-processing



def insert_from_draft():
    pass
    # like insert_whole but single commit, make sure that this will stop processing.  Again, likely use the big
    # common, change commit='single', change post processing




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


def general_insert(insert_cmd, import_lines, commit, connect):
    with cursors.Commander(connect, commit=commit) as cmdr:
        for one_line in import_lines:
            cmdr.do_cmd(insert_cmd, one_line)
    return cmdr.success, cmdr.history


def run_database_commands_as_group(builder, connect, commit):
    with cursors.Commander(connect, commit=commit) as cmdr:
        for cmdstring in builder.values():
            cmdr.do_cmd(cmdstring)
    return cmdr.success, cmdr.history
