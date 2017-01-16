from collections import OrderedDict


class SQLQueryMakerException(Exception):
    def __init__(self, *args):
        super().__init__(args)
        self.reasons = args


def extract_sql_query_cmds(line_generator):
    sql_queries = OrderedDict()
    for aline in line_generator:
        queryname = aline['query name']
        if queryname:
            sql_queries[queryname] = current_query = SQL_Query(queryname, aline)
        else:
            current_query.add_parameter(aline)
    return sql_queries


class SQL_Query(object):
    def __init__(self, query_name, aline):
        self.query_name = query_name
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
    def create_query_cmd_string(self):
        essentials = '\n\t'.join(self.sql_cmd_fragments)
        if self.query_variables_in_psycopg2_format:
            sql_variables = '\n\tvaluelist ' + ', '.join(self.query_variables_in_psycopg2_format)
            return essentials + sql_variables
        else:
            return essentials


