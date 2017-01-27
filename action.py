import file_utilities
import sentry


def poll_imports(imports_path):
    imports_gen = file_utilities.spreadsheet_keyvalue_generator(imports_path)
    for location in imports_gen:
        table, to_do, path = location['table'], location['action'], location['path']
        new, changed, missing = sentry.take_roll_of_new_changes_and_missing(path)
    return [(table, to_do, path), (new, changed, missing)]


def look_for_changes(a_path):
    new, changed, missing = sentry.take_roll_of_new_changes_and_missing()