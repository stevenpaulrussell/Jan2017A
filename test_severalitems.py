import unittest
import os

import file_utilities

local_path = '/Users/steve/'
test_source_directory = 'TestItemsForJan2017A'
test_yaml_filename = 'test_yaml_file'
perm_spreadsheets_filename = 'perm_spreadsheets_test.xls'

test_yaml_path = os.path.join(local_path, test_yaml_filename)
test_source_path = os.path.join(local_path, test_source_directory)
test_perm_spreadsheets_path = os.path.join(test_source_path, perm_spreadsheets_filename)

yaml_test_dictionary = {'perm_spreadsheets': test_perm_spreadsheets_path,
                        'db_spec': 1,
                        'closed_and_mirrored_spreadsheets': 2,
                        'open_spreadsheets': 3}


class Test_test_readiness(unittest.TestCase):
  def test_test_source_path(self):
    self.assertTrue(os.path.exists(test_source_path))
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
  def test_can_get_a_generator(self):
    mydirectory = file_utilities.read_yaml(test_yaml_path)
    perm_spreadsheets_directory_path = mydirectory['perm_spreadsheets']
    data_generator = file_utilities.spreadsheet_keyvalue_generator(perm_spreadsheets_directory_path)
    first_line = data_generator.__next__()
    self.assertTrue('table' in first_line.keys())
    self.assertTrue(first_line['table'] == 'person')



if __name__ == '__main__':
  unittest.main()
