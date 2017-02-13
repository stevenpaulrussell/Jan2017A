import os
import json
from collections import OrderedDict

import file_utilities
import filemoves

SENTRY_FILE_NAME = '.sentry'
IMPORT_WHOLE_ACTION_NAME = 'import whole'
IMPORT_BY_LINE_ACTION_NAME = 'import by line'


work_list = []              # Read by program importing this file


class SentryException(Exception):
    """Placeholder for telemetry and also for debugging"""


class General_Imports(object):
    """Super class holding logic and variable for doing psycopg2 sql imports using spreadsheets"""
    COMMIT_SELECT = {IMPORT_WHOLE_ACTION_NAME: 'group', IMPORT_BY_LINE_ACTION_NAME: 'single', 'test': False}
    def __init__(self, table_name, import_directory, file_name):
        self.table_name = table_name
        self.import_directory = import_directory
        self.file_name = file_name
        self.file_path = os.path.join(import_directory, file_name)
        author = 'from spreadsheet or cloud AAA'
        self.command_keys = dict(author=author, source_file=file_name, commit=self.commit)
        self.build_line = dict(filename=file_name, story=author, author=author, incorporated='2015/12/26')

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


class Whole_Spreadsheet_Imports(General_Imports):
    def __init__(self, table_name, import_directory, file_name):
        self.action = IMPORT_WHOLE_ACTION_NAME
        self.commit = General_Imports.COMMIT_SELECT[self.action]
        super(Whole_Spreadsheet_Imports, self).__init__(table_name, import_directory, file_name)

    def success(self):
        destination_alias = 'archive/{}'.format(self.table_name)
        dest = filemoves.copy_file_path_to_alias_named_directory(self.file_path, destination_alias)
        if dest:
            os.remove(self.file_path)

    def failure(self, history):
        fail_path = os.path.join(self.import_directory, 'ErRoR_{}'.format(self.file_name))
        file_utilities.write_to_xlsx_using_gen_of_dicts_as_source(self.gen_for_failure_spreadsheet(history), fail_path)


class Line_At_A_Time_Imports(General_Imports):
    def __init__(self, table_name, import_directory, file_name):
        self.action = IMPORT_BY_LINE_ACTION_NAME
        self.commit = General_Imports.COMMIT_SELECT[self.action]
        self.previously_imported_lines = []
        self.newly_imported_lines = []
        self.failed_line = None
        super(Line_At_A_Time_Imports, self).__init__(table_name, import_directory, file_name)

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
        remaining = remaining or [OrderedDict([(key, ' ') for key in self.newly_imported_lines[0].keys()])]
        file_utilities.write_to_xlsx_using_gen_of_dicts_as_source((l for l in remaining), self.file_path)

    def update_archive_file(self):
        archive_directory_path = os.join(file_utilities.get_path_from_alias('archive'), self.table_name)
        archive_path = os.path.join(archive_directory_path, self.file_name)
        if os.path.exists(archive_path):
            self.previously_imported_lines = [l for l in file_utilities.spreadsheet_keyvalue_generator(archive_path)]
        to_rewrite = [line for line in self.previously_imported_lines + self.newly_imported_lines]
        if to_rewrite:
            file_utilities.write_to_xlsx_using_gen_of_dicts_as_source((l for l in to_rewrite), archive_path)


def poll_imports():
    import_listings = file_utilities.key_values_from_alias('imports_locator')
    for import_listing in import_listings:
        path_to_import_directory = os.path.join(import_listing['base'], import_listing['path'])
        new, different, missing = take_roll_of_new_changes_and_missing(path_to_import_directory)
        if any((new, different)):
            enlist_work(new, different, import_listing)
            break


def enlist_work(new, different, import_listing):
    if import_listing['action'] == IMPORT_WHOLE_ACTION_NAME:
        enlist_whole_table_work(new, different, import_listing)
    elif import_listing['action'] == IMPORT_BY_LINE_ACTION_NAME:
        enlist_line_at_a_time_work(new, different, import_listing)
    else:
        raise SentryException('to_do "{}" in {} not allowed'.format(import_listing['action'], import_listing['path']))


def enlist_whole_table_work(new, different, import_listing):


    table, import_directory = import_listing['table'], import_listing['path']


    for import_file_name in new:
        work_list.append(Whole_Spreadsheet_Imports(table, import_directory, import_file_name))
    if different:
        raise SentryException('{} changed in {} not allowed'.format(different, import_directory))


def enlist_line_at_a_time_work(new, different, import_listing):
    table, import_directory = import_listing['table'], import_listing['path']
    for import_file_name in new:
        work_list.append(Line_At_A_Time_Imports(table, import_directory, import_file_name))
    for import_file_name in different:
        work_list.append(Line_At_A_Time_Imports(table, import_directory, import_file_name))


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
