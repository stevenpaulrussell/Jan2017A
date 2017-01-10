import unittest
import os


import read_directory


local_path = '/Users/steve/'
test_yaml_filename = 'test_yaml_file'
yaml_test_dictionary = {'one': 1, 'two': 2}


class Test_yaml_functions(unittest.TestCase):
  def setUp(self):
    self.test_yaml_path = os.path.join(local_path, test_yaml_filename)
    with open(self.test_yaml_path,'w') as fp:
        read_directory.write_yaml(yaml_test_dictionary, fp)

  def tearDown(self):
    os.remove(self.test_yaml_path)

  def test_did_yaml_correctly(self):
    test_data = read_directory.read_yaml(self.test_yaml_path)
    self.assertEqual(test_data, yaml_test_dictionary)


class Test_read_directory(unittest.TestCase):
  def setUp(self):
      self.mydirectory = read_directory.read_directory()

  def test_can_get_db_specs(self):
    self.assertIn('db_spec', self.mydirectory.keys())

  def test_two(self):
    self.assertIn('open_spreadsheets', self.mydirectory.keys())

  def test_three(self):
    self.assertIn('mirrored_spreadsheets', self.mydirectory.keys())


class Test_read_db_spec(unittest.TestCase):
  def setUp(self):
    mydirectory = read_directory.read_directory()
    self.db_spec_path = mydirectory['db_spec']




if __name__ == '__main__':
  unittest.main()