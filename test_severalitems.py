import unittest

import read_directory


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

  def test_can_import_db_spec(self):
    self.assertFalse('Finish the test')



if __name__ == '__main__':
  unittest.main()