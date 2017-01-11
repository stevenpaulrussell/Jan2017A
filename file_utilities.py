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
    print(spreadsheet_path)
    for a_row in read_excel_rows_as_dict(spreadsheet_path):
        yield a_row



def read_excel_rows_as_dict(afilepath, comment_row_on_top=False):
    all_rows = read_excel_rows(afilepath)
    all_rows_as_dictionary = []
    key_row = 1 if comment_row_on_top else 0
    keys = all_rows[key_row]
    unique_keys = set(keys)
    assert len(keys) == len(unique_keys)
    for arow in all_rows[key_row + 1:]:
        row_as_dictionary = dict(zip(keys, arow))
        all_rows_as_dictionary.append(row_as_dictionary)
    return all_rows_as_dictionary


def read_excel_rows(afilepath):
    xbook = xlrd.open_workbook(afilepath)
    xsheet = xbook.sheet_by_index(0)
    all_rows = []
    for row_number in range(xsheet.nrows):
        arow = xsheet.row_values(row_number)
        if any(arow):
            cleaned_row = [excel_item_cleaner(item) for item in arow]
            all_rows.append(cleaned_row)
    xbook.release_resources()
    return all_rows

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


def write_lists_to_excel(filepath, list_of_lists):
    assert filepath[-5:] == '.xlsx'
    workbook = xlsxwriter.Workbook(filepath)
    centerwrapformat = workbook.add_format({'text_wrap': True, 'center_across': True})
    worksheet = workbook.add_worksheet()
    for arow, alist in enumerate(list_of_lists):
        for col, item in enumerate(alist):
            worksheet.write(arow, col, item, centerwrapformat)
    workbook.close()




