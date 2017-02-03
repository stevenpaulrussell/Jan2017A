import unittest

import dataqueda_constants
import action
import setup_common_for_test

connect = dataqueda_constants.LOCAL

path_to_listings = setup_common_for_test.read_test_locations()
print('path_to_listings', path_to_listings)


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
        success, history = action.make_database_tables(path_to_listings=path_to_listings, connect=connect)
        tables = action.get_current_tableset(connect=connect)
        self.assertTrue(success)
        self.assertIn('person', tables)


class DoIncrementalAddsToTables(unittest.TestCase):
    """
    Adding a spreadsheet to a directory results in an action detecting the addition, finding the right table for
    data insertion, finding the conditions to commit the insertion and what to do about 'mirroring', doing the
    insertion (presume no errors for now), and reporting the results.

    Need to specify the directories, how they chain, how they instruct
    """

if __name__ == '__main__':
    unittest.main()
