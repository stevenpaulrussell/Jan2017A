import file_utilities
import sentry


def poll_imports(imports_path):
    work_list = []
    imports_gen = file_utilities.spreadsheet_keyvalue_generator(imports_path)
    for location in imports_gen:
        table, to_do, path = location['table'], location['action'], location['path']
        new, changed, missing = sentry.take_roll_of_new_changes_and_missing(path)
        if any((new, changed, missing)):
            work_list.append((table, to_do, path, new, changed, missing))
    return work_list
