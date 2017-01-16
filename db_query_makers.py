from collections import OrderedDict


class SQLQueryMakerException(Exception):
    def __init__(self, *args):
        super().__init__(args)
        self.reasons = args


def extract_sql_query_cmds(line_generator):
    sql_queries = OrderedDict()
    for aline in line_generator:
        print('***', aline.keys())
        queryname = aline['query name']
        if queryname:
            sql_queries[queryname] = current_query = Sql_Query(queryname)
        else:
            current_query.add_parameter(aline)
    return sql_queries


class Sql_Query(object):
    def __init__(self, aline):
        self.query_name = aline[0]
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
    def create_query_cmd_string(self):
        creator = '\n\t'.join(self.sql_cmd_fragments)
        if self.psycopg2_variable_elements:
            sql_variables = '\n\tvaluelist ' + ', '.join(self.psycopg2_variable_elements)
            return creator + sql_variables
        else:
            return creator


