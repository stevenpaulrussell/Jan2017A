import unittest

import dataqueda_constants
import action
import setup_common_for_test

connect = dataqueda_constants.LOCAL

path_to_listings = setup_common_for_test.read_test_locations()


class RebuildDatabaseFromBaseDocuments(unittest.TestCase):
    def test_destroy_database(self):
        tables = action.get_current_tableset(connect=connect)
        if not tables:
            print('test_destroy_database has nothing to destroy')
        else:

            success, history = action.destroy_database_tables(tables, connect=connect)

            self.assertTrue(success)
            self.assertEqual(action.get_current_tableset(connect=connect), set())

    def test_can_destroy_and_rebuild_tables(self):
        tables = action.get_current_tableset(connect=connect)
        action.destroy_database_tables(tables, connect=connect)

        successt, historyt = action.make_database_tables(path_to_listings=path_to_listings, connect=connect)
        successv, historyv = action.make_database_views(path_to_listings=path_to_listings, connect=connect)
        tables = action.get_current_tableset(connect=connect)

        self.assertTrue(successt)
        self.assertTrue(successv)
        self.assertIn('person', tables)
        self.assertIn('CREATE VIEW', historyv[0][0][0])


class RespondToImportsAddsSimple(unittest.TestCase):
    def setUp(self):
        tables = action.get_current_tableset(connect=connect)
        action.destroy_database_tables(tables, connect=connect)
        action.make_database_tables(path_to_listings=path_to_listings, connect=connect)
        action.make_database_views(path_to_listings, connect=connect)

    def test_can_import_whole_sheet(self):
        pass
        # put a file into

if __name__ == '__main__':
    unittest.main()
