import os
import unittest

import action
import setup_common_for_test

import dataqueda_constants

test_directory = setup_common_for_test.read_test_locations()
imports_path = test_directory['imports_locator']


class Test_Actions_Can_Destroy_And_Create_DB(unittest.TestCase):
    def setUp(self):
        self.tableset = action.get_current_tableset(connect=dataqueda_constants.LOCAL)

    def test_can_retrieve_tables(self):
        if self.tableset:
            self.assertIn('person', self.tableset)
        else:
            print('No tables seen in test_action.Test_Actions_Can_Destroy_And_Create_DB.test_can_retrieve_tables')

    def test_destroy_database_tables(self):
        if self.tableset:
            success, history = action.destroy_database_tables(self.tableset, connect=dataqueda_constants.LOCAL)
            self.assertTrue(success)
            (first_command, vars), first_psycop_response = history[0]
            self.assertIn('DROP TABLE IF EXISTS', first_command)
            self.assertEqual(vars, ())
            self.assertFalse(first_psycop_response)
        else:
            print('No tables to destroy in '
                  'test_action.Test_Actions_Can_Destroy_And_Create_DB.test_destroy_database_tables')

    def test_can_create_database_tables(self):
        if self.tableset:
            action.destroy_database_tables(self.tableset, connect=dataqueda_constants.LOCAL)
        success, history = action.make_database_tables(test_directory, connect=dataqueda_constants.LOCAL)
        tableset = action.get_current_tableset(connect=dataqueda_constants.LOCAL)
        (first_command, vars), first_psycop_response = history[0]
        self.assertIn('person', tableset)
        self.assertTrue(success)
        self.assertIn('CREATE TABLE person', first_command)
        self.assertEqual(vars, ())
        self.assertFalse(first_psycop_response)

    def test_can_make_views(self):
        success, history = action.make_database_views(test_directory, connect=dataqueda_constants.LOCAL)
        (first_command, vars), first_psycop_response = history[0]
        self.assertTrue(success)
        self.assertIn('CREATE VIEW', first_command)
        self.assertEqual(vars, ())
        self.assertFalse(first_psycop_response)


if __name__ == '__main__':
    unittest.main()
