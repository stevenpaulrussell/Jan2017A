import os
import time
import json

import file_utilities

SENTRY_FILE_NAME = '.sentry'


changed_list = []


class Changed(object):
    selector = {
        ('import whole','new'): ('import whole commit', 'group'),

    }
    def __init__(self, table_name, to_do, import_directory, file_name, file_change):
        self.table_name = table_name
        self.to_do = to_do
        self.import_directory = import_directory
        self.file_name = file_name
        self.file_change = file_change
        self.file_path = os.path.join(import_directory, file_name)
        author = 'work.Something got from directory shares or from imports_locator spreadsheet'
        self.command_dict = dict(author=author, source_file=file_name)
        self.build_line = dict(filename=file_name, story=author, author=author, incorporated='2015/12/26')
        changed_list.append(self)

    @property
    def command_keys(self):
        if self.select in ('import whole commit', ):
            self.command_dict['commit'] = 'group'
        else:
            pass
        return self.command_dict

    @property
    def import_lines(self):
        return file_utilities.spreadsheet_keyvalue_generator(self.file_path)

    @property
    def select(self):
        if (self.to_do, self.file_change) in [('import whole','new'),]:
            return 'import whole commit'





def poll_imports(imports_path):
    imports_gen = file_utilities.spreadsheet_keyvalue_generator(imports_path)
    for location in imports_gen:
        table_name, to_do, path = location['table'], location['action'], location['path']
        new, different, missing = take_roll_of_new_changes_and_missing(path)
        if new:
            for file_name in new:
                Changed(table_name, to_do, path, file_name, 'new')
        if different:
            for file_name in different:
                Changed(table_name, to_do, path, file_name, 'different')
        if missing:
            for file_name in missing:
                Changed(table_name, to_do, path, file_name, 'missing')
        if any((new, different, missing)):
            break



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
