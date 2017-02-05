import os
import json

import file_utilities
import filemoves

SENTRY_FILE_NAME = '.sentry'
changed_list = []
path_to_listings = None

def poll_imports():
    imports_path = path_to_listings['imports_locator']
    imports_gen = file_utilities.spreadsheet_keyvalue_generator(imports_path)
    for location in imports_gen:
        table_name, to_do, path = location['table'], location['action'], location['path']
        new, different, missing = take_roll_of_new_changes_and_missing(path)
        if new and to_do == 'import whole':
            for file_name in new:
                Whole_Spreadsheet_Imports(table_name, to_do, path, file_name)
        if new and to_do == 'import by line':
            for file_name in new:
                Line_At_A_Time_Imports(table_name, to_do, path, file_name)
        if different and to_do == 'import by line':
            for file_name in different:
                Line_At_A_Time_Imports(table_name, to_do, path, file_name)
        if missing:
            pass
        if any((new, different)):
            break


class Any_Changed(object):
    COMMIT_SELECT = {'import whole': 'group', 'import by line': 'single', 'test': False}
    def __init__(self, table_name, to_do, import_directory, file_name):
        changed_list.append(self)
        self.table_name = table_name
        self.import_directory = import_directory
        self.file_name = file_name
        self.file_path = os.path.join(import_directory, file_name)
        author = 'from spreadsheet or cloud AAA'
        self.command_keys = dict(author=author, source_file=file_name, commit=Any_Changed.COMMIT_SELECT[to_do])
        self.build_line = dict(filename=file_name, story=author, author=author, incorporated='2015/12/26')
        self.get_specialized(to_do)

    def gen_for_failure_spreadsheet(self, history):
        for index, ((cmd, vars), error) in enumerate(history):
            keyed_values = vars[0]
            keyed_values.update(self.groom_psycopg_error_message(error))
            yield keyed_values

    def groom_psycopg_error_message(self, psycopg_error_msg):
        short_error, error_detail = psycopg_error_msg.split('DETAIL:')
        short_error = short_error.replace("'", '').replace('\\n', '')
        error_detail = error_detail.replace(",", '').replace('\\n', '')
        return {'error': short_error, 'error_detail': error_detail}

    @property
    def import_lines(self):
        return file_utilities.spreadsheet_keyvalue_generator(self.file_path)


class Whole_Spreadsheet_Imports(Any_Changed):
    """This will make a default object, but do nothing with it for now.  Use if we want to act on missing files """
    def get_specialized(self, to_do):
        self.action = 'import whole'

    def success(self):
        destination_alias = 'archive/{}'.format(self.table_name)
        dest = filemoves.copy_file_path_to_alias_named_directory(self.file_path, destination_alias, path_to_listings)
        if dest:
            os.remove(self.file_path)

    def failure(self, history):
        fail_path = os.path.join(self.import_directory, 'ErRoR_{}'.format(self.file_name))
        file_utilities.write_to_xlsx_using_gen_of_dicts_as_source(self.gen_for_failure_spreadsheet(history), fail_path)


class Line_At_A_Time_Imports(Any_Changed):
    """This will make a default object, but do nothing with it for now.  Use if we want to act on missing files """
    def get_specialized(self, to_do):
        self.action = 'import by line'
        self.previously_imported_lines = []
        self.newly_imported_lines = []
        self.failed_line = None

    def success(self, one_line):
        one_line.update({'error': ' ', 'error_detail': ' '})
        self.newly_imported_lines.append(one_line)

    def failure(self, history):
        (cmd, vars), error = history[0]
        self.failed_line = vars[0]
        self.failed_line.update(self.groom_psycopg_error_message(error))

    def done(self):
        self.update_import_file()
        self.update_archive_file()

    def update_import_file(self):
        remaining = [self.failed_line] if self.failed_line else []
        pass_by = len(self.newly_imported_lines)
        for index, a_line in enumerate(self.import_lines):
            if index > pass_by:
                remaining.append(a_line)
        file_utilities.write_to_xlsx_using_gen_of_dicts_as_source((l for l in remaining), self.file_path)

    def update_archive_file(self):
        archive_directory_alias = 'archive/{}'.format(self.table_name)
        archive_directory_path = path_to_listings[archive_directory_alias][:-2]
        archive_path = os.path.join(archive_directory_path, self.file_name)
        if os.path.exists(archive_path):
            self.previously_imported_lines = [l for l in file_utilities.spreadsheet_keyvalue_generator(archive_path)]
        to_rewrite = (line for line in self.previously_imported_lines + self.newly_imported_lines)
        file_utilities.write_to_xlsx_using_gen_of_dicts_as_source(to_rewrite, archive_path)



def take_roll_of_new_changes_and_missing(apath):
    previous_file_data = load_json_from_sentry_file(apath)
    previous_file_names = set(previous_file_data.keys())
    current_file_data = get_current_file_stats(apath)
    current_file_names = set(current_file_data.keys())
    new = current_file_names - previous_file_names
    missing = previous_file_names - current_file_names
    persisted = current_file_names.intersection(previous_file_names)
    changed = set()
    for file_name in persisted:
        if current_file_data[file_name] != previous_file_data[file_name]:
            changed.add(file_name)
    dump_json_to_sentry_file(apath, current_file_data)
    return new, changed, missing


def get_current_file_stats(apath):
    current_file_data = {}
    for file_name in os.walk(apath).__next__()[-1]:
        if file_name[0] == '.':
            continue
        if 'ErRoR_' in file_name:
            continue
        current_file_data[file_name] = os.stat(os.path.join(apath, file_name)).st_mtime
    return current_file_data


def load_json_from_sentry_file(apath):
    try:
        with open(os.path.join(apath, SENTRY_FILE_NAME), 'r') as fp:
            return json.load(fp)
    except FileNotFoundError:
        return {}


def dump_json_to_sentry_file(apath, previous_file_data):
    with open(os.path.join(apath, SENTRY_FILE_NAME), 'w') as fp:
        json.dump(previous_file_data, fp)
