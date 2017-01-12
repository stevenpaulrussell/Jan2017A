import os
import collections

import yaml
import xlrd


class InputSpreadsheetException(Exception):
    def __init__(self, *args, **kwds):
        super().__init__(args, kwds)
        self.reasons = args

def read_yaml(yaml_path):
    with open(yaml_path,'r') as fp:
        data = yaml.safe_load(fp)
    return data


def write_yaml(data, yaml_path):
    yaml.safe_dump(data, yaml_path)


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
            yield dict(zip(column_headers, cleaned_row))
    xbook.release_resources()


def write_lists_to_excel(filepath, list_of_lists):
    assert filepath[-5:] == '.xlsx'
    workbook = xlsxwriter.Workbook(filepath)
    centerwrapformat = workbook.add_format({'text_wrap': True, 'center_across': True})
    worksheet = workbook.add_worksheet()
    for arow, alist in enumerate(list_of_lists):
        for col, item in enumerate(alist):
            worksheet.write(arow, col, item, centerwrapformat)
    workbook.close()




