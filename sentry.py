import os
import json
from collections import OrderedDict
from datetime import datetime

import file_utilities

SENTRY_FILE_NAME = '.sentry'
IMPORT_WHOLE_ACTION_NAME = 'import whole'
IMPORT_BY_LINE_ACTION_NAME = 'import by line'
IMPORT_TEST = 'test only'


work_list = []              # Read by program importing this file


class SentryException(Exception):
    """Placeholder for telemetry and also for debugging"""


class General_Imports(object):
    """Super class holding logic and variable for doing psycopg2 sql imports using spreadsheets"""
    def __init__(self, import_directory, file_name, work_spec):
        self.import_directory = import_directory
        self.file_name = file_name
        self.file_path = os.path.join(import_directory, file_name)
        self.table_name = work_spec['table']
        author = work_spec.setdefault('author', 'from spreadsheet or cloud AAA')
        story = work_spec.setdefault('story', 'from spreadsheet or cloud AAA')
        todays_date = datetime.today().strftime('%Y/%m/%d')   # '2015/12/26'
        self.command_keys = dict(author=author, source_file=file_name)
        self.build_line = OrderedDict()
        self.build_line['filename'] = file_name
        self.build_line['story'] = story
        self.build_line['author'] = author
        self.build_line['incorporated'] = todays_date
        self.commit = 'NOTE ---> Must be one of False, "single", "group"  <----'

    @property
    def import_lines(self):
        return file_utilities.spreadsheet_keyvalue_generator(self.file_path)

    def append_import_to_archive_import_locator(self):
        new_line = self.build_line.copy()
        new_line.update(table=self.table_name)
        archive_import_locator_path = file_utilities.get_path_from_alias('archive_import_locator')
        file_utilities.append_to_xlsx_using_list_of_lines([new_line], archive_import_locator_path)

    def gen_for_failure_spreadsheet(self, history):
        for index, ((cmd, vars), error) in enumerate(history):
            keyed_values = vars[0]
            keyed_values.update(self.groom_psycopg_error_message(error))
            yield keyed_values

    def groom_psycopg_error_message(self, psycopg_error_msg):
        try:
            short_error, error_detail = psycopg_error_msg.split('DETAIL:')
        except ValueError:
            short_error, error_detail = psycopg_error_msg, ' '
        except AttributeError:
            short_error, error_detail = ' ', ' '
        short_error = short_error.replace("'", '').replace('\\n', '')
        error_detail = error_detail.replace(",", '').replace('\\n', '')
        return {'error': short_error, 'error_detail': error_detail}



class Whole_Spreadsheet_Imports(General_Imports):
    def __init__(self, import_directory, file_name, work_spec):
        super(Whole_Spreadsheet_Imports, self).__init__(import_directory, file_name, work_spec)
        self.action = IMPORT_WHOLE_ACTION_NAME
        self.commit = 'group'

    def success(self, *args):
        archive_directory_name = 'archive_directory/{}'.format(self.table_name)
        archive_directory_path = file_utilities.get_path_from_alias(archive_directory_name)
        file_utilities.copy_file_path_to_dir(self.file_path, archive_directory_path)
        os.remove(self.file_path)
        self.append_import_to_archive_import_locator()

    def failure(self, history):
        fail_path = os.path.join(self.import_directory, 'ErRoR_{}'.format(self.file_name))
        file_utilities.write_to_xlsx_using_gen_of_dicts_as_source(self.gen_for_failure_spreadsheet(history), fail_path)


class Test_Only_Spreadsheet_Imports(Whole_Spreadsheet_Imports):
    def __init__(self, import_directory, file_name, work_spec):
        super(Test_Only_Spreadsheet_Imports, self).__init__(import_directory, file_name, work_spec)
        self.commit = False

    def success(self, history):
        success_path = os.path.join(self.import_directory, 'SuCcEsS_{}'.format(self.file_name))
        file_utilities.write_to_xlsx_using_gen_of_dicts_as_source(self.gen_for_failure_spreadsheet(history), success_path)


class Line_At_A_Time_Imports(General_Imports):
    def __init__(self, import_directory, file_name, work_spec):
        super(Line_At_A_Time_Imports, self).__init__(import_directory, file_name, work_spec)
        self.action = IMPORT_BY_LINE_ACTION_NAME
        self.commit = 'single'
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
        remaining = remaining or [OrderedDict([(key, ' ') for key in self.newly_imported_lines[0].keys()])]
        file_utilities.write_to_xlsx_using_gen_of_dicts_as_source((l for l in remaining), self.file_path)

    def update_archive_file(self):
        archive_directory_name = 'archive_directory/{}'.format(self.table_name)
        archive_directory_path = file_utilities.get_path_from_alias(archive_directory_name)
        archive_file_path = os.path.join(archive_directory_path, self.file_name)
        if file_utilities.append_to_xlsx_using_list_of_lines(self.newly_imported_lines, archive_file_path):
            self.append_import_to_archive_import_locator()


def poll_imports():
    import_listings = file_utilities.key_values_from_alias('imports_locator')
    for import_listing in import_listings:
        path_to_import_directory = os.path.join(import_listing['base'], import_listing['path'])
        if not os.path.exists(path_to_import_directory):
            continue
        new, different, missing = take_roll_of_new_changes_and_missing(path_to_import_directory)
        if any((new, different)):
            enlist_work(new, different, path_to_import_directory, work_spec=import_listing)
            break


def enlist_work(new, different, path_to_import_directory, work_spec):
    if work_spec['action'] == IMPORT_WHOLE_ACTION_NAME:
        for import_file_name in new:
            work_list.append(Whole_Spreadsheet_Imports(path_to_import_directory, import_file_name, work_spec))
        if different:
            raise SentryException('{} changed in {} not allowed'.format(different, path_to_import_directory))
    elif work_spec['action'] == IMPORT_BY_LINE_ACTION_NAME:
        for import_file_name in new:
            work_list.append(Line_At_A_Time_Imports(path_to_import_directory, import_file_name, work_spec))
        for import_file_name in different:
            work_list.append(Line_At_A_Time_Imports(path_to_import_directory, import_file_name, work_spec))
    elif work_spec['action'] == IMPORT_TEST:
        for import_file_name in new:
            work_list.append(Test_Only_Spreadsheet_Imports(path_to_import_directory, import_file_name, work_spec))
        for import_file_name in different:
            work_list.append(Line_At_A_Time_Imports(path_to_import_directory, import_file_name, work_spec))
    else:
        raise SentryException('to_do "{}" in {} not allowed'.format(work_spec['action'], work_spec['path']))


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
        if any([file_name[0] == '.', 'ErRoR_' in file_name, 'SuCcEsS_' in file_name]):
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
