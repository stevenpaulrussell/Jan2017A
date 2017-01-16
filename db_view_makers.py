from collections import OrderedDict


class SQLViewMakerException(Exception):
    def __init__(self, *args):
        super().__init__(args)
        self.reasons = args


def extract_sql_view_cmds(line_generator):
    sql_views = OrderedDict()
    for aline in line_generator:
        viewname = aline['view name']
        if viewname:
            sql_views[viewname] = current_view = SQL_View(viewname)
        else:
            current_view.add_parameter(aline)
    return sql_views


class Sql_View(object):
    def __init__(self, aline):
        self.view_name = aline[0]
        self.view_create_cmd = 'CREATE VIEW {} AS\n\t'.format(self.view_name)
        self.sql_cmd_fragments = []
        self.psycopg2_variable_elements = []
        self.increase(aline)

    def increase(self, aline):
        sql_cmd_fragment, psycopg2_variable_element = aline[1:3]
        if not sql_cmd_fragment:
            return
        self.sql_cmd_fragments.append(sql_cmd_fragment)
        if psycopg2_variable_element:
            self.psycopg2_variable_elements.append(psycopg2_variable_element)

    @property
    def create_view_cmd_string(self):
        creator = self.view_create_cmd + '\n\t'.join(self.sql_cmd_fragments)
        if self.psycopg2_variable_elements:
            sql_variables = '\n\tvaluelist ' + ', '.join(self.psycopg2_variable_elements)
            return creator + sql_variables
        else:
            return creator

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

