import unittest
import os
from itertools import chain

import file_utilities
import setup_common_for_test as common


class Test_Am_Ready_For_Test(unittest.TestCase):
    def test_have_good_spreadsheet_of_test_locations(self):
        self.assertIn('db_template', common.test_directory)
        self.assertIn('dropbox_test_directory', common.test_directory)
        self.assertIn('imports_locator', common.test_directory)


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


if __name__ == '__main__':
    unittest.main()
