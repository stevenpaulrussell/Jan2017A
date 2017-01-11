import os
import collections

import yaml
import xlrd



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
        return
    column_headers = xsheet.row_values(0)
    if xsheet.nrows == 1:
        return dict(zip(column_headers, [None]*len(column_headers)))
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




