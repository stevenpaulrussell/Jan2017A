import os
import time

import unittest

import action
import dataqueda_constants
import setup_common_for_test

from dataqueda_constants import LOCAL


class MyTestCase(unittest.TestCase):
    def setUp(self):
        setup_common_for_test.clean_directories()
        tableset = action.get_current_tableset(connect=LOCAL)
        action.destroy_database_tables(tableset, connect=LOCAL)
        action.make_database_tables(connect=LOCAL)
        action.make_database_views(connect=LOCAL)
        print('Ready to go in test_running')

    def test_go_for_10_minutes(self):
        for count in range(1200):
            if not count%30:
                print(count)
            action.do_a_work_item(LOCAL)
            time.sleep(.5)
        self.assertTrue('Already done')



if __name__ == '__main__':
    unittest.main()
