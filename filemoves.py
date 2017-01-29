import os
import shutil

import file_utilities


def move_alias_to_path(alias, locator, path):
    pass


def find_imports_directories_matching_rules(locator_path, **matchlist):
    imports_gen = file_utilities.spreadsheet_keyvalue_generator(locator_path)
    return  [line for line in imports_gen if set(matchlist.items()).issubset(line.items())]
