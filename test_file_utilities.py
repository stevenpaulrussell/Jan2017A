import unittest
import os
from itertools import chain

import file_utilities
import setup_common_for_test as common


class Test_Am_Ready_For_Test(unittest.TestCase):
    def test_have_good_spreadsheet_of_test_locations(self):
        test_paths = common.read_test_locations()
        self.assertIn('db_template', test_paths)
        self.assertIn('dropbox_test', test_paths)
        self.assertIn('imports_locator', test_paths)


class Test_can_read_a_spreadsheet(unittest.TestCase):
    def test_various_problems_sheet(self):
        data_generator = file_utilities.spreadsheet_keyvalue_generator(common.test_various_problems_spreadsheets_path)
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
        data_generator = file_utilities.spreadsheet_keyvalue_generator(common.test_bad_header_spreadsheet_path)
        with self.assertRaises(file_utilities.InputSpreadsheetException) as context:
            data_generator.__next__()
        self.assertIn('has at least one empty header column', context.exception.reasons[0])

    def test_header_only_sheet(self):
        data_generator = file_utilities.spreadsheet_keyvalue_generator(common.test_header_only_spreadsheet_path)
        with self.assertRaises(file_utilities.InputSpreadsheetException) as context:
            data_generator.__next__()
        self.assertIn('spreadsheet is only headers', context.exception.reasons[0])

    def test_empty_spreadsheet_sheet(self):
        with self.assertRaises(file_utilities.InputSpreadsheetException) as context:
            data_generator = file_utilities.spreadsheet_keyvalue_generator(common.test_empty_spreadsheet_path)
            data_generator.__next__()
        self.assertIn('spreadsheet is empty', context.exception.reasons[0])


class TestWritingToAn_xlsx(unittest.TestCase):
    def setUp(self):
        self.test_paths = common.read_test_locations()
        self.data_generator = file_utilities.spreadsheet_keyvalue_generator(self.test_paths['person_table_example'])
        self.test_write_path = os.path.join(common.test_source_path, 'TEST_WRITE.xlsx')

    def tearDown(self):
        if os.path.exists(self.test_write_path):
            os.remove(self.test_write_path)

    def test_copy(self):
        file_utilities.write_to_xlsx_using_gen_of_dicts_as_source(self.data_generator, self.test_write_path)
        original_gen = file_utilities.spreadsheet_keyvalue_generator(self.test_paths['person_table_example'])
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
            if aline['last'].lower() == 'garcia':
                return 'No {} allowed'.format(aline['last'])

        source_gen = file_utilities.spreadsheet_keyvalue_generator(self.test_paths['person_table_example'])
        filtered_gen = file_utilities.gen_by_filtering_from_gen_list(source_gen, stop_last_name_moss, msg_store)
        file_utilities.write_to_xlsx_using_gen_of_dicts_as_source(filtered_gen, self.test_write_path)
        copy_gen = file_utilities.spreadsheet_keyvalue_generator(self.test_write_path)
        contents = [copy_item for copy_item in copy_gen]
        self.assertEqual(len(contents), 6)
        self.assertEqual(self.msg, 'No Garcia allowed')


if __name__ == '__main__':
    unittest.main()
