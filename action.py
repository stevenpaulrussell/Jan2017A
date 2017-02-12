import os
from collections import OrderedDict

import sentry
import cursors
import sql_command_library
import file_utilities

BUILD_HISTORY_TABLE = 'build_history'

class ActionException(Exception):
    """For help with debugging fow now """


def do_a_work_item(connect):
    sentry.poll_imports()
    if sentry.work_list:
        change = sentry.work_list.pop(0)
        insert_cmd = sql_command_library.read_db_insertion_commands()[change.table_name]
        if change.action == 'import whole':
            return import_whole_sheet(change, insert_cmd, connect)
        elif change.action == 'import by line':
            return import_line_at_a_time(change, insert_cmd, connect)
        else:
            msg = 'change.action "{}" not recognized'.format(change.action)
            raise ActionException(msg)


def import_whole_sheet(change, insert_cmd, connect):
        success, history = general_insert(insert_cmd, change.import_lines, connect=connect, **change.command_keys)
        if success:
            add_to_build_history(change.build_line, connect=connect)
            change.success()
        else:
            change.failure(history)
        return success, history


def import_line_at_a_time(change, insert_cmd, connect):
        for one_line in change.import_lines:
            success, history = single_insert(insert_cmd, one_line, connect=connect, **change.command_keys)
            if success:
                change.success(one_line)
            else:
                change.failure(history)  # history will show the error
                break # stop the line iteration
        change.done()
        return success, history


def add_to_build_history(build_line, connect):
    insert_cmd = sql_command_library.read_db_insertion_commands()[BUILD_HISTORY_TABLE]
    with cursors.Commander(connect, commit='group') as cmdr:
        cmdr.do_cmd(insert_cmd, build_line)
    if not cmdr.success:
        raise cursors.CommanderException(cmdr.history)
    return


def get_current_tableset(connect):
    return cursors.Commander(connect=connect).tableset


def destroy_database_tables(tableset, connect):
    with cursors.Commander(connect, commit='group') as cmdr:
        for table in tableset:
            cmdr.do_cmd(cmdr.drop_table_string.format(table))
    return cmdr.success, cmdr.history


def make_database_tables(connect):
    table_builder = sql_command_library.read_db_creation_commands()
    success, history = run_database_commands_as_group(table_builder, connect, commit='group')
    return success, history


def make_database_views(connect):
    view_builder = sql_command_library.read_view_creation_commands()
    success, history = run_database_commands_as_group(view_builder, connect, commit='group')
    return success, history


def run_database_queries(path_to_listings, connect):
    troubles = []
    report_directory = file_utilities.get_path_from_alias('sql_reports_directory')
    query_builder = sql_command_library.read_query_creation_commands()
    for query_name, query_string in query_builder.items():
        with cursors.Commander(connect) as cmdr:
            cmdr.do_query(query_string)
        success, history, report = cmdr.success, cmdr.history, cmdr.query_response_gen
        report = [line for line in report]
        report_gen = (line for line in report)
        if success:
            report_path = os.path.join(report_directory, query_name + '.xlsx')
            if len(report) > 1:
                file_utilities.write_to_xlsx_using_gen_of_dicts_as_source(report_gen, report_path)
            else:
                try:
                    os.remove(report_path)
                except FileNotFoundError:
                    pass
        else:
            troubles.append(history)
    tpath = path_to_listings['sql_query_trouble']
    if troubles:
        file_utilities.write_to_xlsx_using_gen_of_dicts_as_source((t for t in troubles), tpath)
        print('\nWrite trouble report {}'.format(troubles))
    else:
        try:
            os.remove(tpath)
        except FileNotFoundError:
            pass
    return not troubles, history



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


def single_insert(insert_cmd, one_line, commit, connect, **kwds):
    with cursors.Commander(connect, commit=commit, **kwds) as cmdr:
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

