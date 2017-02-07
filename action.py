import sentry
import cursors
import sql_command_library

BUILD_HISTORY_TABLE = 'build_history'

class ActionException(Exception):
    """For help with debugging fow now """


def do_a_work_item(path_to_listings, connect):
    sentry.path_to_listings = path_to_listings
    sentry.poll_imports()
    if sentry.work_list:
        change = sentry.work_list.pop(0)
        insert_cmd = sql_command_library.read_db_insertion_commands(path_to_listings)[change.table_name]
        if change.action == 'import whole':
            return import_whole_sheet(change, insert_cmd, path_to_listings, connect)
        elif change.action == 'import by line':
            return import_line_at_a_time(change, insert_cmd, connect)
        else:
            msg = 'change.action "{}" not recognized'.format(change.action)
            raise ActionException(msg)


def import_whole_sheet(change, insert_cmd, path_to_listings, connect):
        success, history = general_insert(insert_cmd, change.import_lines, connect=connect, **change.command_keys)
        if success:
            add_to_build_history(change.build_line, path_to_listings=path_to_listings, connect=connect)
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


def add_to_build_history(build_line, path_to_listings, connect):
    insert_cmd = sql_command_library.read_db_insertion_commands(path_to_listings)[BUILD_HISTORY_TABLE]
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


def make_database_tables(path_to_listings, connect):
    table_builder = sql_command_library.read_db_creation_commands(path_to_listings)
    success, history = run_database_commands_as_group(table_builder, connect, commit='group')
    return success, history


def make_database_views(path_to_listings, connect):
    view_builder = sql_command_library.read_view_creation_commands(path_to_listings)
    success, history = run_database_commands_as_group(view_builder, connect, commit='group')
    return success, history


def run_database_queries(path_to_listings, connect):
    query_builder = sql_command_library.read_query_creation_commands(path_to_listings)
    success, history = run_database_commands_as_group(query_builder, connect, commit='group')
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




def make_queries(local_connect):
    message_list = ['Running queries']
    report_dirname = 'Reports'
    cmdr = Commander(DATABASENAME, local_connect)
    query_cmds = read_queries(DATAQUEDA_AWS_BUCKET)
    for a_query_name in query_cmds.keys():
        message_list.append(a_query_name)
        create_query_cmd_string = query_cmds[a_query_name].create_query_cmd_string
        possible_error = cmdr.do_cmd(create_query_cmd_string)
        if possible_error:
            message_list.append(possible_error)
            continue
        try:
            results = cmdr.cur.fetchall()
        except Exception as E:
            message_list.append(repr(E))
            continue
        report_filename = '{}.xlsx'.format(a_query_name)  # just the query name.. for now!
        report_path = os.path.join(local_report_dir, report_filename)
        make_excel_report(report_path, create_query_cmd_string, results)
        aws.move_local_file_to_s3(report_path, DATAQUEDA_AWS_BUCKET, '{}/{}'.format(report_dirname, report_filename))
        message_list.append('Successfully wrote {} to aws'.format(report_filename))
    cmdr.close()
    write_action_result_to_aws(message_list, 'make_queries_result.txt')


def make_excel_report(filepath, query_cmd, results):
    first_line = query_cmd.split('\n')[0]
    query_headers = extract_lower_case_words(first_line)
    list_of_lists = [query_headers]
    for one_line in results:
        list_of_lists += [list(one_line)]
    excels.write_lists_to_excel(filepath, list_of_lists)


def extract_lower_case_words(astring):
    """A helper routine solely for make_excel_report"""
    query_headers = []
    for sub_string in astring.split():
        character_list = [character for character in sub_string if character.islower()]
        if character_list:
            query_headers.append(''.join(character_list))
    return query_headers


