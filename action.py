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
    if poll_and_check_for_work():
        work = sentry.work_list.pop()
        try:
            work_spec = {'import whole': import_whole_sheet, 'import by line': import_line_at_a_time}[work.action]
        except KeyError:
            raise ActionException('change.action "{}" not recognized'.format(work.action))
        else:
            insert_cmd = sql_command_library.read_db_insertion_commands()[work.table_name]
            success, history = work_spec(work, insert_cmd, connect)
            new_work = poll_and_check_for_work()
            if new_work:
                worked_file_name = os.path.splitext(work.file_name)[0]
                new_work_file_name = os.path.splitext(new_work.file_name)[0]
                if worked_file_name == new_work_file_name:
                    sentry.work_list.pop()
            return success, history


def poll_and_check_for_work():
    sentry.poll_imports()
    if sentry.work_list:
        return sentry.work_list[-1]


def import_whole_sheet(work, insert_cmd, connect):
    with cursors.Commander(connect, work.commit) as cmdr:
        for one_line in work.import_lines:
            one_line.update(work.command_keys)
            cmdr.do_cmd(insert_cmd, one_line)
    if cmdr.success:
        work.success(cmdr.history)
        add_to_build_history(work.build_line, connect=connect)
    else:
        work.failure(cmdr.history)
    return cmdr.success, cmdr.history


def import_line_at_a_time(work, insert_cmd, connect):
    for one_line in work.import_lines:
        with cursors.Commander(connect, work.commit) as cmdr:
            one_line.update(work.command_keys)
            cmdr.do_cmd(insert_cmd, one_line)
        if cmdr.success:
            work.success(one_line)
        else:
            work.failure(cmdr.history)
            break
    work.done()
    return cmdr.success, cmdr.history


def add_to_build_history(build_line, connect):
    if build_line:
        insert_cmd = sql_command_library.read_db_insertion_commands()[BUILD_HISTORY_TABLE]
        with cursors.Commander(connect, commit='group') as cmdr:
            cmdr.do_cmd(insert_cmd, build_line)
        if not cmdr.success:
            raise cursors.CommanderException(cmdr.history)



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


def run_database_queries(connect):
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
    tpath = os.path.join(report_directory, 'sql_query_trouble.xlsx')
    if troubles:
        file_utilities.write_to_xlsx_using_gen_of_dicts_as_source((t for t in troubles), tpath)
        print('\nWrite trouble report {}'.format(troubles))
    else:
        try:
            os.remove(tpath)
        except FileNotFoundError:
            pass
    return not troubles, history



def run_database_commands_as_group(builder, connect, commit):
    with cursors.Commander(connect, commit=commit) as cmdr:
        for cmdstring in builder.values():
            cmdr.do_cmd(cmdstring)
    return cmdr.success, cmdr.history

