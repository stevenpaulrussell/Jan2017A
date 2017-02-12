import os
import collections

import xlrd
import xlsxwriter


KNOWN_SYSTEMS = ('steve air', )

file_listings = {}  # Actual values are set via a global variable in some function, maybe read_file_listings below.


class InputSpreadsheetException(Exception):
    def __init__(self, *args, **kwds):
        super().__init__(args, kwds)
        self.reasons = args

class FileMovesSurprise(Exception):
    """Flag any unusual cases"""


def read_file_listings(path_to_listings):
    """This is called by some main program to read in locations of everything """
    global file_listings
    file_listings = {}
    for aline in spreadsheet_keyvalue_generator(path_to_listings):
        alias = aline.pop('alias')
        file_listings[alias] = dict(aline)


def get_path_from_alias(alias):
    spec = file_listings[alias]
    if not spec['system'] in KNOWN_SYSTEMS:
        raise FileMovesSurprise('alias "{}" asking for unknown system "{}"'.format(alias, spec['system']))
    return os.path.join(spec['base'], spec['path'])



def copy_file_path_to_alias_named_directory(source_file_path, alias, locator):
    """Copy specified file to a directory named by alias in locator.  Use for test and moving imports after done."""
    dest_path = locator[alias]
    dest_dir, file_name_must_be_star = os.path.split(dest_path)
    if file_name_must_be_star != '*':
        msg = 'alias {} shows path {} filename "{}" not "*"'.format(alias, dest_path, file_name_must_be_star)
        raise FileMovesSurprise(msg)
    return copy_file_path_to_dir(source_file_path, dest_dir)


def copy_alias_to_path(alias, locator, path_for_copy):
    """Copy a file named in a 'locator' spreadsheet to a directory specified by path_for_copy. Return copied to path"""
    source_path = locator[alias]
    return copy_file_path_to_dir(source_path, path_for_copy)


def copy_file_path_to_dir(source_file_path, dir_path):
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


def spreadsheet_keyvalue_generator(spreadsheet_path):
    def excel_item_cleaner(item):
        """
        Assumes all excel values seen will be strings or floats.
        Changes excel '' to None.  Excel expresses integer values as floats: fix that.
        Removes leading and trailing spaces to avoid hidden errors:  ' name' vs 'name'.
        """
        try:
            return item.strip() or None
        except AttributeError:
            # because excel expresses 42 as 42.0 !
            return int(item) if int(item) == item else item
    xbook = xlrd.open_workbook(spreadsheet_path)
    xsheet = xbook.sheet_by_index(0)
    if xsheet.nrows == 0:
        raise InputSpreadsheetException('<{}> spreadsheet is empty'.format(spreadsheet_path))
    column_headers = [excel_item_cleaner(item) for item in xsheet.row_values(0)]
    if not all(column_headers):
        msg1 = '<{}> spreadsheet has at least one empty header column.'.format(spreadsheet_path)
        msg2 = 'seeing (cleaned) headers: {} '.format(column_headers)
        raise InputSpreadsheetException(msg1, msg2)
    if xsheet.nrows == 1:
        raise InputSpreadsheetException('<{}> spreadsheet is only headers'.format(spreadsheet_path))
    for row_number in range(1, xsheet.nrows):
        arow = xsheet.row_values(row_number)
        if any(arow):
            cleaned_row = [excel_item_cleaner(item) for item in arow]
            yield collections.OrderedDict(zip(column_headers, cleaned_row))
    xbook.release_resources()


def write_to_xlsx_using_gen_of_dicts_as_source(gen_of_dicts, dest_file_path):
    assert dest_file_path[-5:] == '.xlsx'
    workbook = xlsxwriter.Workbook(dest_file_path)
    centerwrapformat = workbook.add_format({'text_wrap': True, 'center_across': True})
    worksheet = workbook.add_worksheet()

    def write_a_row(row, alist):
        for col, item in enumerate(alist):
            if item is None:
                item = ' '
            worksheet.write(row, col, item, centerwrapformat)

    keyvalues = gen_of_dicts.__next__()
    write_a_row(0, keyvalues.keys())
    write_a_row(1, keyvalues.values())
    for gen_number, keyvalues in enumerate(gen_of_dicts):
        write_a_row(gen_number + 2, keyvalues.values())
    workbook.close()


