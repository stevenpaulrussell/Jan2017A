from collections import OrderedDict


def extract_sql_table_cmds(line_generator):
    sql_tables = OrderedDict()
    for aline in line_generator:
        tablename = aline['table name']
        if tablename:
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

    @property
    def insert_cmdstring(self):
        l1 = ', '.join(self.column_names)
        l2 = '%({})s, '.format(self.column_names[0])
        for aname in self.column_names[1:-1]:
            l2 = l2 + '%({})s, '.format(aname)
        l2 = l2 + '%({})s'.format(self.column_names[-1])
        lead = 'INSERT INTO {}'.format(self.tablename)
        cmdstring = '{}\n\t({})\nVALUES\n\t({})'.format(lead, l1, l2)
        return cmdstring

    @property
    def createtable_cmdstring(self):
        if not self.primary_key_contraint:
            msg = 'Table with name {} missing PK to get PRIMARY KEY'.format(self.tablename)
            print(msg)
        lead = 'CREATE TABLE {}\n\t(\n'.format(self.tablename)
        datastring = ',\n'.join(self.data_items)
        firstpart = lead + datastring + ',\n' + self.primary_key_contraint
        tail = '\n\t)'
        if self.constraints:
            return firstpart + ',\n\t' + ',\n\t'.join(self.constraints) + tail
        else:
            return firstpart + tail

    @property
    # So that each table also is a report -- make the right query string
    def create_query_cmd_string(self):
        query_string = 'SELECT '
        query_string += ', '.join(self.column_names)
        query_string += '\n\tFROM {}'.format(self.tablename)
        return query_string



