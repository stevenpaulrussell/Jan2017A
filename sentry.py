import os
import json

import file_utilities

SENTRY_FILE_NAME = '.sentry'
changed_list = []


class Any_Changed(object):
    COMMIT_SELECT = {'import whole': 'group', 'import_lines': 'single', 'test': False}
    def __init__(self, table_name, to_do, import_directory, file_name):
        changed_list.append(self)
        self.table_name = table_name
        self.file_path = os.path.join(import_directory, file_name)
        author = 'hidalgo from imports_locator spreadsheet or cloud services AAA'
        self.command_keys = dict(author=author, source_file=file_name, commit=Any_Changed.COMMIT_SELECT[to_do])
        self.build_line = dict(filename=file_name, story=author, author=author, incorporated='2015/12/26')
        self.action = None
        self.get_specialized(to_do)

    @property
    def import_lines(self):
        return file_utilities.spreadsheet_keyvalue_generator(self.file_path)


class File_Is_New(Any_Changed):
    """This will make a default object, but do nothing with it for now.  Use if we want to act on missing files """
    def get_specialized(self, to_do):
        self.action = 'import whole'
    def success(self):
        pass
        # move from where is to x (routine) unless this is a future add one line at a time in which case no move
    def failure(self, history):
        pass
    def done(self):
        pass


class File_Is_Different(Any_Changed):
    """This will make a default object, but do nothing with it for now.  Use if we want to act on missing files """
    def get_specialized(self, to_do):
        self.action = 'import using mirror'
    def success(self):
        pass # store the success
    def failure(self, history):
        pass
    def done(self):
        pass
                # re-write mirror for any successes.  avoid doing this in batch by iterating on insert, not general insert?
                # move or delete from where is (routine)



def poll_imports(imports_path):
    imports_gen = file_utilities.spreadsheet_keyvalue_generator(imports_path)
    for location in imports_gen:
        table_name, to_do, path = location['table'], location['action'], location['path']
        new, different, missing = take_roll_of_new_changes_and_missing(path)
        if new:
            for file_name in new:
                File_Is_New(table_name, to_do, path, file_name)
        if different:
            for file_name in different:
                File_Is_Different(table_name, to_do, path, file_name)
        if missing:
            pass
        if any((new, different)):
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
