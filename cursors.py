import os
import psycopg2
from collections import OrderedDict

import dataqueda_constants


class Commander(object):
    drop_table_string = "DROP TABLE IF EXISTS {} CASCADE"
    drop_view_string = "DROP VIEW IF EXISTS {} CASCADE"

    def __init__(self, connect, **kwds):
        self.my_kwd = kwds
        self.con = psycopg2.connect(**connect)
        self.cur = self.con.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def commit(self):
        self.con.commit()

    def close(self):
        self.cur.close()
        self.con.close()

    def do_cmd(self, cmd, *myvars):
        if 'valuelist' in cmd:
            real_cmd, varstring = cmd.split('valuelist')
            myvars = [var.strip() for var in varstring.split(',')]
            if real_cmd.count('(%s)') != len(myvars):
                msg = 'In dbcmds.cmd_extractor, have mismatch between variables and places in query "{}"'.format(cmd)
                raise dataqueda_constants.DBFormatException(msg)
            return self._do_cmd(real_cmd, myvars)
        else:
            return self._do_cmd(cmd, *myvars)

    def _do_cmd(self, cmd, *myvars):
        try:
            self.cur.execute(cmd, *myvars)
        except Exception as e:
            msg = 'Exception "<{}>"\nPsycopg2 (cmd, vars) were cmd "<{}>". vars "<{}>"'.format(repr(e), cmd, myvars)
            self.con.rollback()
            return msg

    @property
    def tableset(self):
        string_that_lists_tables = "SELECT relname FROM pg_class WHERE relkind='r' AND relname !~ '^(pg_|sql_)'"
        self.do_cmd(string_that_lists_tables)
        tupleslist = self.cur.fetchall()
        return set([item[0] for item in tupleslist])




def run_update(tablename, keyed_values_list, commit):
    the_keys = keyed_values_list[0].keys()
    file_header = list(the_keys) + ['message']
    integral_list = [file_header]
    failure_list = [file_header]
    insert_cmdstring = read_master()[tablename].insert_cmdstring
    cmdr = Commander()
    for keyed_values in keyed_values_list:
        value_list = list(keyed_values.values())
        failure_msg = cmdr.do_cmd(insert_cmdstring, keyed_values)
        if not failure_msg:
            integral_list.append(value_list)
        else:
            value_list.append(failure_msg if len(failure_msg) < 120 else failure_msg[12:132])
            failure_list.append(value_list)
            integral_list.append(value_list)
    if commit and not len(failure_list) == 1:
        cmdr.commit()
    return failure_list, integral_list


def add_filename_to_build_history(file_name, story='to be added', author='to be added'):
    cmdr = Commander()
    insert_cmdstring = read_master()['build_history'].insert_cmdstring
    insert_values = {'filename': file_name, 'story': story, 'author': author, 'incorporated': '2015/12/26'}
    cmdr.do_cmd(insert_cmdstring, insert_values)
    cmdr.commit()
