import os
import unittest

import action
import sentry
import setup_common_for_test

import dataqueda_constants
import filemoves

test_directory = setup_common_for_test.read_test_locations()
imports_path = test_directory['imports_locator']


class TestRunQueries(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_good_queries_write_reports(self):
        #action.run_database_queries(test_directory, connect=dataqueda_constants.LOCAL)
        self.assertFalse('do this first')

    def test_bad_queries_write_trouble_reports(self):
        action.run_database_queries(test_directory, connect=dataqueda_constants.LOCAL)
        self.assertFalse('do this second')

    def test_null_queries_remove_reports(self):
        #action.run_database_queries(test_directory, connect=dataqueda_constants.LOCAL)
        self.assertFalse('do this third')


if __name__ == '__main__':
    unittest.main()
