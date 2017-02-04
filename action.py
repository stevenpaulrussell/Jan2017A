import sentry
import cursors
import sql_command_library

BUILD_HISTORY_TABLE = 'build_history'


def do_a_work_item(path_to_listings, connect):
    imports_path = path_to_listings['imports_locator']
    sentry.poll_imports(imports_path)
    if sentry.changed_list:
        change = sentry.changed_list.pop(0)
        insert_cmd = sql_command_library.read_db_insertion_commands(path_to_listings)[change.table_name]
        if change.action == 'import whole':
            return import_whole_sheet(change, insert_cmd, path_to_listings, connect)
        elif change.action == 'import using mirror':
            return import_line_at_a_time(change, insert_cmd, connect)


def import_whole_sheet(change, insert_cmd, path_to_listings, connect):
        success, history = general_insert(insert_cmd, change.import_lines, connect=connect, **change.command_keys)
        if success:
            add_to_build_history(change.build_line, path_to_listings=path_to_listings, connect=connect)
            change.success()
        else:
            change.failure(history)
        return success, history


def import_line_at_a_time(change, insert_cmd, connect):
        mirror_location = 'mirror location plug'
        for one_line in change.check_against_mirror(mirror_location):
            success, history = single_insert(insert_cmd, one_line, connect=connect, **change.command_keys)
            if success:
                change.success(one_line)
            else:
                change.failure(history)  # history will show the error
                break # stop the line iteration
        change.done()



def add_to_build_history(build_line, path_to_listings, connect):
    insert_cmd = sql_command_library.read_db_insertion_commands(path_to_listings)[BUILD_HISTORY_TABLE]
    with cursors.Commander(connect, commit='group') as cmdr:
        cmdr.do_cmd(insert_cmd, build_line)
    print('in action.do_a_work_item.add_to_build_history, need an exception watcher on cmdr.success', cmdr.success)
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
