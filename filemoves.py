import os
import shutil

import file_utilities

class FileMovesSurprise(Exception):
    """Flag any unusual cases"""


def copy_alias_to_path(alias, locator, path_for_copy):
    source_path = locator[alias]
    source_file_name = os.path.split(source_path)[-1]
    copied_path = os.path.join(path_for_copy, source_file_name)
    if not os.path.isdir(path_for_copy):
        msg = '{} not a directory, is target for {}'.format(path_for_copy, source_path)
        raise FileMovesSurprise(msg)
    if os.path.exists(copied_path):
        msg = 'Found {} already has {}'.format(path_for_copy, source_file_name)
        raise FileMovesSurprise(msg)
    else:
        shutil.copyfile(source_path, copied_path)
    return copied_path


def find_unique_import_directory_matching_pattern(locator_path, **matchlist):
    matches = find_all_imports_lines_matching_pattern(locator_path, **matchlist)
    if len(matches) != 1:
        msg = 'Found {}, expected exactly 1 match for {}'.format(len(matches), **matchlist)
        raise FileMovesSurprise(msg)
    else:
        return matches[0]['path']


def find_all_imports_lines_matching_pattern(locator_path, **matchlist):
    imports_gen = file_utilities.spreadsheet_keyvalue_generator(locator_path)
    return  [line for line in imports_gen if set(matchlist.items()).issubset(line.items())]

