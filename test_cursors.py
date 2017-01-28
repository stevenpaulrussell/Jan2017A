import unittest

import cursors
import dataqueda_constants
import sql_command_library
import setup_common_for_test


test_directory = setup_common_for_test.read_test_locations()


class MyTestCase(unittest.TestCase):
    def test_am_connecting_locally_and_see_local_tables(self):
        cmdr = cursors.Commander(**dataqueda_constants.LOCAL)
        self.assertTrue(cmdr.tableset)


class CanConnectRemotelyAndMakeTables(unittest.TestCase):
    def setUp(self):
        self.cmdr = cursors.Commander(**dataqueda_constants.REMOTE)

    def tearDown(self):
        self.cmdr.close()

    def test_remote_has_no_tables_to_start(self):
        self.assertFalse(self.cmdr.tableset)

    def test_one_table_making_remote(self):
        self.cmdr.do_cmd(sql_command_library.read_db_creation_commands(test_directory)['person'])
        self.assertTrue(self.cmdr.tableset)
        self.assertIn('person', self.cmdr.tableset)





if __name__ == '__main__':
    unittest.main()
