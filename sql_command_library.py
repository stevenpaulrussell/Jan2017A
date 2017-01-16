import collections
import file_utilities

from test_severalitems import test_db_template_path
from test_severalitems import test_view_template_path
from test_severalitems import test_query_template_path
import db_cmd_makers, db_view_makers, db_query_makers

xx = None

def read_db_creation_commands():
    creation_commands = collections.OrderedDict()
    print('Need to set up directory files and how to fine them.  May test without to start')
    return xx


def write_db_creation_commands():
    global xx
    template_line_gen = file_utilities.spreadsheet_keyvalue_generator(test_db_template_path)
    xx = db_cmd_makers.extract_sql_table_cmds(template_line_gen)
