import os
import psycopg2
from collections import OrderedDict

import dataqueda_constants

class CommanderException(Exception):
    """Raise if a problem with invoking Commander"""


class Commander(object):
    drop_table_string = "DROP TABLE IF EXISTS {} CASCADE"
    drop_view_string = "DROP VIEW IF EXISTS {} CASCADE"
    list_table_string = "SELECT relname FROM pg_class WHERE relkind='r' AND relname !~ '^(pg_|sql_)'"
    legal_kwds = dict(commit=(False, "single", "group"))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __init__(self, connect, **kwds):
        self.my_kwds = kwds
        self._check_kwds()
        self.con = psycopg2.connect(**connect)
        self.cur = self.con.cursor()
        self.cmd_history = []
        self.result_history = []

    def close(self):
        self.success = not any(self.result_history)
        if self.success and self.my_kwds['commit'] == 'group':
            self.con.commit()
        self.cur.close()
        self.con.close()
        self.history = list(zip(self.cmd_history, self.result_history))

    def do_cmd(self, cmd, *myvars):
        self.cmd_history.append((cmd, myvars))
        psycop_response = self._valuelist_cmd(cmd) if 'valuelist' in cmd else self._do_cmd(cmd, *myvars)
        self.result_history.append(psycop_response)

    def _do_cmd(self, cmd, *myvars):
        try:
            self.cur.execute(cmd, *myvars)
        except Exception as e:
            self.con.rollback()
            return repr(e)
        else:
            if self.my_kwds['commit'] == 'single':
                self.con.commit()

    def _valuelist_cmd(self, cmd):
        real_cmd, varstring = cmd.split('valuelist')
        myvars = [var.strip() for var in varstring.split(',')]
        if real_cmd.count('(%s)') != len(myvars):
            msg = 'In dbcmds.cmd_extractor, have mismatch between variables and places in query "{}"'.format(cmd)
            raise dataqueda_constants.DBFormatException(msg)
        result = self._do_cmd(real_cmd, myvars)
        return result

    def _check_kwds(self):
        try:
            if self.my_kwds['commit'] not in Commander.legal_kwds['commit']:
                raise CommanderException('"commit" keyword must be one of "{}"'.format(Commander.legal_kwds))
        except KeyError:
            self.my_kwds['commit'] = False

    @property
    def tableset(self):
        self.do_cmd(Commander.list_table_string)
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
