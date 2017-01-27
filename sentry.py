import os
import time
import json

import file_utilities

SENTRY_FILE_NAME = '.sentry'


work_list = []


class WorkItem(object):
    def __init__(self, table_name, to_do, directory, file_name, file_change):
        self.table_name = table_name
        self.to_do = to_do
        self.directory = directory
        self.file_name = file_name
        self.file_change = file_change
        work_list.append(self)


def poll_imports(imports_path):
    imports_gen = file_utilities.spreadsheet_keyvalue_generator(imports_path)
    for location in imports_gen:
        table_name, to_do, path = location['table'], location['action'], location['path']
        new, changed, missing = take_roll_of_new_changes_and_missing(path)
        if new:
            for file_name in new:
                WorkItem(table_name, to_do, path, file_name, 'new')
        if changed:
            for file_name in changed:
                WorkItem(table_name, to_do, path, file_name, 'changed')
        if missing:
            for file_name in missing:
                WorkItem(table_name, to_do, path, file_name, 'missing')
        if any((new, changed, missing)):
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
