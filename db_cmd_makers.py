from collections import OrderedDict


def extract_sql_table_cmds(line_generator):
    current_table = None
    sql_tables = OrderedDict()
    for aline in line_generator:
        tablename = aline['table name']
        if tablename:
            if current_table:
                current_table.inspect_for_error()
            sql_tables[tablename] = current_table = SQL_Table(tablename)
        else:
            current_table.add_parameter(aline)
    return sql_tables


class SQL_Table(object):
    def __init__(self, tablename):
        self.tablename = tablename
        self.data_items = []
        self.column_names = []
        self.constraints = []

    def add_parameter(self, aline):
        item_name = aline['item name']
        supplement = aline['supplemental strings'] or ''

        def add_to_string(self, item_name, type_string, supplement):
            if supplement:
                new_item = '\t{} {} {}'.format(item_name, type_string, supplement)
            else:
                new_item = '\t{} {}'.format(item_name, type_string)
            self.data_items.append(new_item)

        def add_column_name_and_to_string(self, item_name, type_string, supplement):
            self.column_names.append(item_name)
            add_to_string(self, item_name, type_string, supplement)

        if aline['type'] == 'PK':
            self.primary_key_contraint = '\tCONSTRAINT {} PRIMARY KEY {}'.format(item_name, supplement)
        elif aline['type'] == 'FK':
            self.constraints.append('CONSTRAINT {} FOREIGN KEY {}'.format(item_name, supplement))
        elif aline['type'] == 'ser':
            add_to_string(self, item_name, 'SERIAL', supplement)
        elif aline['type'] == 'int':
            add_column_name_and_to_string(self, item_name, 'INT', supplement)
        elif aline['type'] == 'var':
            add_column_name_and_to_string(self, item_name, 'VARCHAR(80)', supplement)
        elif aline['type'] == 'text':
            add_column_name_and_to_string(self, item_name, 'TEXT', supplement)
        elif aline['type'] == 'date':
            add_column_name_and_to_string(self, item_name, 'DATE', supplement)
        else:
            print('Problem in building table {} with line <{}>'.format(self.tablename, aline))
            print(aline['type'], '\n')

    def inspect_for_error(self):
        print('Debug... am in SQL_Table.inspect_for_errors for table "{}"'.format(self.tablename))

    @property
    def insert_cmdstring(self):
        firstline = 'INSERT INTO {}'.format(self.tablename)
        line_per_column = ', '.join(self.column_names)
        lastline = '%({})s, '.format(self.column_names[0])
        for aname in self.column_names[1:-1]:
            lastline += '%({})s, '.format(aname)
        lastline += '%({})s'.format(self.column_names[-1])
        return '{}\n\t({})\nVALUES\n\t({})'.format(firstline, line_per_column, lastline)

    @property
    def createtable_cmdstring(self):
        firstline = 'CREATE TABLE {}\n\t(\n'.format(self.tablename)
        line_per_column = ',\n'.join(self.data_items)
        essentials = firstline + line_per_column + ',\n' + self.primary_key_contraint
        if self.constraints:
            line_per_constraint = ',\n\t'.join(self.constraints)
            return essentials + ',\n\t' + line_per_constraint + '\n\t)'
        else:
            return essentials + '\n\t)'

    @property
    # So that each table also is a report -- make the right query string
    def create_query_cmd_string(self):
        return 'SELECT ' + ', '.join(self.column_names) + '\n\tFROM {}'.format(self.tablename)



