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
    def test_begin(self):
        success, history = action.run_database_queries(test_directory, connect=dataqueda_constants.LOCAL)
        print(len(history), history[0])
        for item in history:
            print(item)

        self.assertTrue(success)
        self.assertTrue(len(history) > 10)


if __name__ == '__main__':
    unittest.main()
