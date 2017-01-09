from unittest import TestCase

import read_directory

__author__ = 'steve'


class TestRead_directory(TestCase):
  def test_read_directory(self):
    result = read_directory.read_directory()
    self.assertIn('tablespec', result.keys())
