import os.path
import collections

import xlrd
import xlsxwriter


class InputSpreadsheetException(Exception):
    def __init__(self, *args, **kwds):
        super().__init__(args, kwds)
        self.reasons = args


def read_my_directory(directory_path):
    my_gen = spreadsheet_keyvalue_generator(directory_path)
    my_directory = {}
    for aline in my_gen:
        alias = aline.pop('alias')
        my_directory[alias] = dict(aline)
    return my_directory


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


def gen_by_filtering_from_gen_list(a_gen, checker, action=lambda msg: 1):
    for item in a_gen:
        msg = checker(item)
        if msg:
            action(msg)
            break
        else:
            yield item







