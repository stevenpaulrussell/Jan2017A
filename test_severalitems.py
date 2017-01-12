import unittest
import os

import file_utilities

local_path = '/Users/steve/'
test_source_directory = 'TestItemsForJan2017A'
test_yaml_filename = 'test_yaml_file'

bad_header_spreadsheet_test_filename = 'bad_header_spreadsheet_test.xls'
header_only_spreadsheet_test_filename = 'header_only_spreadsheet_test.xls'
various_problems_spreadsheet_test_filename = 'various_problems_spreadsheet_test.xls'
empty_spreadsheet_test_filename = 'empty_spreadsheet_test.xls'

perm_spreadsheets_filename = 'perm_spreadsheets_test.xlsx'

test_yaml_path = os.path.join(local_path, test_yaml_filename)
test_source_path = os.path.join(local_path, test_source_directory)

test_bad_header_spreadsheet_path = os.path.join(test_source_path, bad_header_spreadsheet_test_filename)
test_header_only_spreadsheet_path = os.path.join(test_source_path, header_only_spreadsheet_test_filename)
test_various_problems_spreadsheets_path = os.path.join(test_source_path, various_problems_spreadsheet_test_filename)
test_empty_spreadsheet_path = os.path.join(test_source_path, empty_spreadsheet_test_filename)
test_perm_spreadsheets_path = os.path.join(test_source_path, perm_spreadsheets_filename)


yaml_test_dictionary = {'perm_spreadsheets': test_perm_spreadsheets_path,
                        'db_spec': 1,
                        'closed_and_mirrored_spreadsheets': 2,
                        'open_spreadsheets': 3}


class Test_test_readiness(unittest.TestCase):
  def test_test_source_path(self):
    self.assertTrue(os.path.exists(test_source_path))
    self.assertTrue(os.path.exists(test_bad_header_spreadsheet_path))
    self.assertTrue(os.path.exists(test_header_only_spreadsheet_path))
    self.assertTrue(os.path.exists(test_various_problems_spreadsheets_path))
    self.assertTrue(os.path.exists(test_empty_spreadsheet_path))
    self.assertTrue(os.path.exists(test_perm_spreadsheets_path))


class Test_Do_Setups(unittest.TestCase):
  """Super class for tests in order to not duplicate setup and teardown functions"""
  def setUp(self):
    with open(test_yaml_path, 'w') as fp:
      file_utilities.write_yaml(yaml_test_dictionary, fp)

  def tearDown(self):
    os.remove(test_yaml_path)


class Test_yaml_functions(Test_Do_Setups):
  def test_did_yaml_correctly(self):
    self.assertTrue(os.path.exists(test_yaml_path))
    test_data = file_utilities.read_yaml(test_yaml_path)
    self.assertEqual(test_data, yaml_test_dictionary)


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
  def test_copy(self):
    mydirectory = file_utilities.read_yaml(test_yaml_path)
    data_generator = file_utilities.spreadsheet_keyvalue_generator(test_various_problems_spreadsheets_path)
    test_write_path = os.path.join(test_source_path, 'TEST_WRITE.xlsx')
    file_utilities.write_to_xlsx_using_gen_of_dicts_as_source(data_generator, test_write_path)
    original_gen = file_utilities.spreadsheet_keyvalue_generator(test_various_problems_spreadsheets_path)
    copy_gen = file_utilities.spreadsheet_keyvalue_generator(test_various_problems_spreadsheets_path)
    for source_item in original_gen:
      copy_item = copy_gen.__next__()
      self.assertEqual(source_item, copy_item)

  def test_compare_mirror_with_open_raise_exception_on_problem(self):
    self.assertFalse(42)

  def test_use_open_to_update_mirror_on_test(self):
    self.assertFalse(42)




if __name__ == '__main__':
  unittest.main()
