import unittest

import cursors
import dataqueda_constants
import sql_command_library
import setup_common_for_test


test_directory = setup_common_for_test.read_test_locations()


class MyTestCase(unittest.TestCase):
    def test_am_connecting_locally_and_see_local_tables(self):
        cmdr = cursors.Commander(connect=dataqueda_constants.LOCAL)
        self.assertTrue(cmdr.tableset or cmdr.tableset==set())


class CanConnectRemotely(unittest.TestCase):
    def setUp(self):
        self.cmdr = cursors.Commander(connect=dataqueda_constants.REMOTE)

    def test_can_see_remote_table_structure(self):
        self.assertTrue(self.cmdr.tableset or self.cmdr.tableset==set())





if __name__ == '__main__':
    unittest.main()
