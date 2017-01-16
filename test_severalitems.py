import unittest
import os
from itertools import chain

import file_utilities

local_path = '/Users/steve/'
test_source_directory = 'TestItemsForJan2017A'
test_yaml_filename = 'test_yaml_file'

bad_header_spreadsheet_test_filename = 'bad_header_spreadsheet_test.xls'
header_only_spreadsheet_test_filename = 'header_only_spreadsheet_test.xls'
various_problems_spreadsheet_test_filename = 'various_problems_spreadsheet_test.xls'
empty_spreadsheet_test_filename = 'empty_spreadsheet_test.xls'

perm_spreadsheets_filename = 'perm_spreadsheets_test.xlsx'
person_table_example = 'person_from_TutorsAugust2015.xlsx'
db_template = 'sass0_master2.xls'
view_template = 'sql_views.xls'
query_template = 'sql_queries.xls'

test_yaml_path = os.path.join(local_path, test_yaml_filename)
test_source_path = os.path.join(local_path, test_source_directory)

test_bad_header_spreadsheet_path = os.path.join(test_source_path, bad_header_spreadsheet_test_filename)
test_header_only_spreadsheet_path = os.path.join(test_source_path, header_only_spreadsheet_test_filename)
test_various_problems_spreadsheets_path = os.path.join(test_source_path, various_problems_spreadsheet_test_filename)
test_empty_spreadsheet_path = os.path.join(test_source_path, empty_spreadsheet_test_filename)
test_perm_spreadsheets_path = os.path.join(test_source_path, perm_spreadsheets_filename)
test_person_table_example_path = os.path.join(test_source_path, person_table_example)
test_db_template_path = os.path.join(test_source_path, db_template)
test_view_template_path = os.path.join(test_source_path, view_template)
test_query_template_path = os.path.join(test_source_path, query_template)

yaml_test_dictionary = {'perm_spreadsheets': test_perm_spreadsheets_path,
                        'db_spec': 1,
                        'closed_and_mirrored_spreadsheets': 2,
                        'open_spreadsheets': 3}


class Test_Test_Readiness(unittest.TestCase):
    def test_test_source_path(self):
        self.assertTrue(os.path.exists(test_source_path))
        self.assertTrue(os.path.exists(test_bad_header_spreadsheet_path))
        self.assertTrue(os.path.exists(test_header_only_spreadsheet_path))
        self.assertTrue(os.path.exists(test_various_problems_spreadsheets_path))
        self.assertTrue(os.path.exists(test_empty_spreadsheet_path))
        self.assertTrue(os.path.exists(test_perm_spreadsheets_path))
        self.assertTrue(os.path.exists(test_person_table_example_path))
        self.assertTrue(os.path.exists(test_db_template_path))


class Test_Do_Setups(unittest.TestCase):
    """Super class for tests in order to not duplicate setup and teardown functions"""
    def setUp(self):
        with open(test_yaml_path, 'w') as fp:
            file_utilities.write_yaml(yaml_test_dictionary, fp)

    def tearDown(self):
        os.remove(test_yaml_path)


class Test_Yaml_Functions(Test_Do_Setups):
    def test_did_yaml_correctly(self):
        self.assertTrue(os.path.exists(test_yaml_path))
        test_data = file_utilities.read_yaml(test_yaml_path)
        self.assertEqual(test_data, yaml_test_dictionary)
        print('\n{}\n{}'.format('*'*8, 'Fix up the yaml_test_dictionary in test_severalitems:'))
        for key, value in test_data.items():
            print('\t{}:\t{}'.format(key, value))
        print('*'*8, '\n')


class Test_get_directories_and_db_spec_from_yaml(Test_Do_Setups):
    def setUp(self):
        super().setUp()
        self.mydirectory = file_utilities.read_yaml(test_yaml_path)

    def test_can_get_perm_spreadsheets_directory(self):
        perm_spreadsheets_directory_path = self.mydirectory['perm_spreadsheets']
        self.assertTrue(os.path.exists(perm_spreadsheets_directory_path))

    def test_can_get_db_specs(self):
        db_spec_path = self.mydirectory['db_spec']
        self.assertEqual(db_spec_path, 1)

    def test_can_get_closed_and_mirrored_spreadsheets(self):
        closed_and_mirrored_spreadsheets = self.mydirectory['closed_and_mirrored_spreadsheets']
        self.assertEqual(closed_and_mirrored_spreadsheets, 2)

    def test_can_get_db_specs(self):
        open_spreadsheets = self.mydirectory['open_spreadsheets']
        self.assertEqual(open_spreadsheets, 3)


class Test_can_read_a_spreadsheet(Test_Do_Setups):
    def test_various_problems_sheet(self):
        data_generator = file_utilities.spreadsheet_keyvalue_generator(test_various_problems_spreadsheets_path)
        first_line = data_generator.__next__()
        self.assertEqual(first_line['spaces_in_middle_and_end'], 'the header    and this have    spaces')
        self.assertEqual(first_line['spaces_at_end_only'], 'spaces')
        self.assertEqual(first_line['empty string'], None)
        self.assertEqual(first_line['5 as float'], 5)
        second_line = data_generator.__next__()
        self.assertEqual(second_line['spaces_in_middle_and_end'], 'this comes after empty line')
        self.assertEqual(second_line['spaces_at_end_only'], None)
        self.assertEqual(second_line['empty string'], None)
        self.assertEqual(second_line['5 as float'], None)

    def test_bad_header_sheet(self):
        data_generator = file_utilities.spreadsheet_keyvalue_generator(test_bad_header_spreadsheet_path)
        with self.assertRaises(file_utilities.InputSpreadsheetException) as context:
            data_generator.__next__()
        self.assertIn('has at least one empty header column', context.exception.reasons[0])

    def test_header_only_sheet(self):
        data_generator = file_utilities.spreadsheet_keyvalue_generator(test_header_only_spreadsheet_path)
        with self.assertRaises(file_utilities.InputSpreadsheetException) as context:
            data_generator.__next__()
        self.assertIn('spreadsheet is only headers', context.exception.reasons[0])

    def test_empty_spreadsheet_sheet(self):
        with self.assertRaises(file_utilities.InputSpreadsheetException) as context:
            data_generator = file_utilities.spreadsheet_keyvalue_generator(test_empty_spreadsheet_path)
            data_generator.__next__()
        self.assertIn('spreadsheet is empty', context.exception.reasons[0])

    def test_can_get_a_generator_from_good_sheet_and_yaml(self):
        mydirectory = file_utilities.read_yaml(test_yaml_path)
        perm_spreadsheets_directory_path = mydirectory['perm_spreadsheets']
        data_generator = file_utilities.spreadsheet_keyvalue_generator(perm_spreadsheets_directory_path)
        first_line = data_generator.__next__()
        self.assertTrue('table' in first_line.keys())
        self.assertTrue(first_line['table'] == 'person')


class TestWritingToAn_xlsx(Test_Do_Setups):
    def setUp(self):
        super().setUp()
        self.data_generator = file_utilities.spreadsheet_keyvalue_generator(test_person_table_example_path)
        self.test_write_path = os.path.join(test_source_path, 'TEST_WRITE.xlsx')

    def tearDown(self):
        super().tearDown()
        if os.path.exists(self.test_write_path):
            os.remove(self.test_write_path)

    def test_copy(self):
        file_utilities.write_to_xlsx_using_gen_of_dicts_as_source(self.data_generator, self.test_write_path)
        original_gen = file_utilities.spreadsheet_keyvalue_generator(test_person_table_example_path)
        copy_gen = file_utilities.spreadsheet_keyvalue_generator(self.test_write_path)
        for source_item in original_gen:
            copy_item = copy_gen.__next__()
            self.assertEqual(source_item, copy_item)

    def test_gen_by_filtering_from_gen_list(self):
        mylist_a = ['a', 'b', None]
        mylist_b = [1, {}, 'string', 2, 3]
        sum_list = mylist_a + mylist_b

        def complain_about_2(item):
            if item == 2:
                return 'Do not accept any 2s!'

        def list_a():
            for item in mylist_a:
                yield item

        def list_b():
            for item in mylist_b:
                yield item

        def msg_print(msg):
            self.msg = msg
        filtered_gen = file_utilities.gen_by_filtering_from_gen_list(chain(list_a(), list_b()),
                                                                     complain_about_2, msg_print)
        filtrate = [result for result in filtered_gen]
        self.assertEqual(filtrate, sum_list[:6])
        self.assertEqual(self.msg, 'Do not accept any 2s!')

    def test_gen_by_filtering_from_gen_list_to_make_excel_file(self):
        def msg_store(msg):
            self.msg = msg

        def stop_last_name_moss(aline):
            if aline['last'].lower() == 'moss':
                return 'No {} allowed'.format(aline['last'])

        source_gen = file_utilities.spreadsheet_keyvalue_generator(test_person_table_example_path)
        filtered_gen = file_utilities.gen_by_filtering_from_gen_list(source_gen, stop_last_name_moss, msg_store)
        file_utilities.write_to_xlsx_using_gen_of_dicts_as_source(filtered_gen, self.test_write_path)
        copy_gen = file_utilities.spreadsheet_keyvalue_generator(self.test_write_path)
        contents = [copy_item for copy_item in copy_gen]
        self.assertEqual(len(contents), 5)
        self.assertEqual(self.msg, 'No Moss allowed')


class TestWorkingWith_DB_Template(unittest.TestCase):
    def test_smoke_test_of_template(self):
        template_line_gen = file_utilities.spreadsheet_keyvalue_generator(test_db_template_path)
        first_line = template_line_gen.__next__()
        self.assertIn('table name', first_line)








if __name__ == '__main__':
    unittest.main()
