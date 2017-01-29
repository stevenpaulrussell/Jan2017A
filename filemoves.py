import os
import shutil

import file_utilities

class FileMovesSurprise(Exception):
    """Flag any unusual cases"""


def copy_file_path_to_alias_named_directory(source_file_path, alias, locator):
    """Copy specified file to a directory named by alias in locator.  Use for test and moving imports after done."""
    dest_path = locator[alias]
    dest_dir, file_name_must_be_star = os.path.split(dest_path)
    if file_name_must_be_star != '*':
        msg = 'alias {} shows path {} filename "{}" not "*"'.format(alias, dest_path, file_name_must_be_star)
        raise FileMovesSurprise(msg)
    return _copy_file_path_to_dir(source_file_path, dest_dir)


def copy_alias_to_path(alias, locator, path_for_copy):
    """Copy a file named in a 'locator' spreadsheet to a directory specified by path_for_copy. Return copied to path"""
    source_path = locator[alias]
    return _copy_file_path_to_dir(source_path, path_for_copy)


def _copy_file_path_to_dir(source_file_path, dir_path):
    """Common pattern used for alias and import copying """
    source_file_name = os.path.split(source_file_path)[-1]
    copied_path = os.path.join(dir_path, source_file_name)
    if not os.path.isdir(dir_path):
        msg = '{} not a directory, is target for {}'.format(dir_path, source_file_path)
        raise FileMovesSurprise(msg)
    if os.path.exists(copied_path):
        msg = 'Found {} already has {}'.format(dir_path, source_file_name)
        raise FileMovesSurprise(msg)
    else:
        shutil.copyfile(source_file_path, copied_path)
    return copied_path


def find_unique_import_directory_matching_pattern(locator_path, **matchlist):
    """Returns path of unique import directory, or raises exception if unique not found."""
    matches = find_all_imports_lines_matching_pattern(locator_path, **matchlist)
    if len(matches) != 1:
        msg = 'Found {}, expected exactly 1 match for {}'.format(len(matches), **matchlist)
        raise FileMovesSurprise(msg)
    else:
        return matches[0]['path']


def find_all_imports_lines_matching_pattern(locator_path, **matchlist):
    """Pattern matching aka sql select. Mostly for test, find import directories with wanted properties"""
    imports_gen = file_utilities.spreadsheet_keyvalue_generator(locator_path)
    return  [line for line in imports_gen if set(matchlist.items()).issubset(line.items())]

