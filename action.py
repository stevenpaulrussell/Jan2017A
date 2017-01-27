import os

import file_utilities
import sentry


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
        new, changed, missing = sentry.take_roll_of_new_changes_and_missing(path)
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

