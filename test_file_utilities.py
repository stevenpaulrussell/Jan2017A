import unittest
import os

import file_utilities
import setup_common_for_test as common


class UseAliasForAccessingDirectoriesAndFiles(unittest.TestCase):
    def test_alias_function_returns_a_path(self):
        test_file_path = file_utilities.get_path_from_alias('empty_spreadsheet_test')
        self.assertTrue(os.path.exists(test_file_path))


class Test_Am_Ready_For_Test(unittest.TestCase):
    def test_have_good_spreadsheet_of_test_locations(self):
        self.assertIn('db_template', common.test_directory)
        self.assertIn('dropbox_test_directory', common.test_directory)
        self.assertIn('imports_locator', common.test_directory)

    def test_have_consistent_test_setup(self):
        for alias in common.test_directory:
            test_file_path = file_utilities.get_path_from_alias(alias)
            if alias == 'archive_import_locator':
                continue
            # if not os.path.exists(test_file_path):
            #     print('failed', alias, test_file_path)
            self.assertTrue(os.path.exists(test_file_path))

class Test_can_read_a_spreadsheet(unittest.TestCase):
    def test_various_problems_sheet(self):
        test_file_path = file_utilities.get_path_from_alias('various_problems_test')
        data_generator = file_utilities.spreadsheet_keyvalue_generator(test_file_path)
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
        test_file_path = file_utilities.get_path_from_alias('bad_header_test')
        data_generator = file_utilities.spreadsheet_keyvalue_generator(test_file_path)
        with self.assertRaises(file_utilities.InputSpreadsheetException) as context:
            data_generator.__next__()
        self.assertIn('has at least one empty header column', context.exception.reasons[0])

    def test_header_only_sheet(self):
        test_file_path = file_utilities.get_path_from_alias('header_only_test')
        data_generator = file_utilities.spreadsheet_keyvalue_generator(test_file_path)
        with self.assertRaises(file_utilities.InputSpreadsheetException) as context:
            data_generator.__next__()
        self.assertIn('spreadsheet is only headers', context.exception.reasons[0])

    def test_empty_spreadsheet_sheet(self):
        test_file_path = file_utilities.get_path_from_alias('empty_spreadsheet_test')
        with self.assertRaises(file_utilities.InputSpreadsheetException) as context:
            data_generator = file_utilities.spreadsheet_keyvalue_generator(test_file_path)
            data_generator.__next__()
        self.assertIn('spreadsheet is empty', context.exception.reasons[0])


class TestWritingToAn_xlsx(unittest.TestCase):
    def setUp(self):
        self.test_file_path = file_utilities.get_path_from_alias('person_table_example')
        self.data_generator = file_utilities.spreadsheet_keyvalue_generator(self.test_file_path)
        test_write_directory = file_utilities.get_path_from_alias('test_write_directory')
        self.test_write_path = os.path.join(test_write_directory, 'TEST_WRITE.xlsx')

    def tearDown(self):
        if os.path.exists(self.test_write_path):
            os.remove(self.test_write_path)

    def test_copy(self):
        file_utilities.write_to_xlsx_using_gen_of_dicts_as_source(self.data_generator, self.test_write_path)
        original_gen = file_utilities.spreadsheet_keyvalue_generator(self.test_file_path)
        copy_gen = file_utilities.spreadsheet_keyvalue_generator(self.test_write_path)
        for source_item in original_gen:
            copy_item = copy_gen.__next__()
            self.assertEqual(source_item, copy_item)

    def test_xl_append_works(self):
        my_lines = [line for line in self.data_generator]
        file_utilities.write_to_xlsx_using_gen_of_dicts_as_source((l for l in my_lines), self.test_write_path)
        to_append = (my_lines[0], my_lines[1])
        file_utilities.append_to_xlsx_using_list_of_lines(to_append, self.test_write_path)

        new_contents = [l for l in file_utilities.spreadsheet_keyvalue_generator(self.test_write_path)]

        self.assertEqual(new_contents[:2], new_contents[-2:])
        self.assertEqual(new_contents[1], new_contents[-1])


class TestFileMovesAndAlias(unittest.TestCase):
    def setUp(self):
        common.clean_directories(verbose=True)

    def tearDown(self):
        common.clean_directories(verbose=True)

    def test_move_to_import_folder_using_locator_sheet(self):
        dest_path = file_utilities.get_path_from_alias('import whole person directory')
        source_path = file_utilities.get_path_from_alias('person_table_example')
        file_name = os.path.split(source_path)[-1]
        path, dirs, files = os.walk(dest_path).__next__()
        self.assertNotIn(file_name, files)
        file_utilities.copy_file_path_to_dir(source_path, dest_path)
        path, dirs, files = os.walk(dest_path).__next__()
        self.assertEqual(path, dest_path)
        self.assertEqual(dirs, [])
        self.assertIn(file_name, files)




if __name__ == '__main__':
    unittest.main()
