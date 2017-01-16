from collections import OrderedDict


class SQLViewMakerException(Exception):
    def __init__(self, *args):
        super().__init__(args)
        self.reasons = args


def extract_sql_view_cmds(line_generator):
    sql_views = OrderedDict()
    for aline in line_generator:
        view_name = aline['view name']
        if view_name:
            sql_views[view_name] = current_view = SQL_View(view_name, aline)
        else:
            current_view.add_parameter(aline)
    return sql_views


class SQL_View(object):
    def __init__(self, view_name, aline):
        self.view_name = view_name
        self.sql_cmd_fragments = []
        self.query_variables_in_psycopg2_format = []
        self.add_parameter(aline)

    def add_parameter(self, aline):
        sql_cmd_fragment = aline['sql command']
        psycopg2_variable_element = aline['value list'] or ''
        self.sql_cmd_fragments.append(sql_cmd_fragment)
        if psycopg2_variable_element:
            self.query_variables_in_psycopg2_format.append(psycopg2_variable_element)

    @property
    def create_view_cmd_string(self):
        essentials = 'CREATE VIEW {} AS\n\t'.format(self.view_name) + '\n\t'.join(self.sql_cmd_fragments)
        if self.query_variables_in_psycopg2_format:
            sql_variables = '\n\tvaluelist ' + ', '.join(self.query_variables_in_psycopg2_format)
            return essentials + sql_variables
        else:
            return essentials

    @property
    # So that each view also is a report -- make the right query string
    def create_query_cmd_string(self):
        query_list = []
        view_column_string = self.sql_cmd_fragments[0].strip('SELECT ')
        view_column_list = view_column_string.split(',')
        for item in view_column_list:
            field_name = item.split('.')[1] if '.' in item else item
            query_list.append(field_name)
        column_string = ', '.join(query_list)
        query_string = 'SELECT {}\n\tFROM {}'.format(column_string, self.view_name)
        return query_string

