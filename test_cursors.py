import unittest

import cursors
import dataqueda_constants
import sql_command_library
import setup_common_for_test


test_directory = setup_common_for_test.read_test_locations()


class MyTestCase(unittest.TestCase):
    def test_am_connecting_locally_and_see_local_tables(self):
        cmdr = cursors.Commander()
        self.assertTrue(dataqueda_constants.LOCAL_CONNECT)
        self.assertTrue(cmdr.tableset)

    def test_aws_connects_and_sees_no_tables(self):
        cmdr = cursors.Commander(False)
        self.assertFalse(cmdr.tableset)

    def test_aws_connect_gets_exception_on_nonsense(self):
        cmdr = cursors.Commander(connect_to_local_database=False)
        exception_msg = cmdr.do_cmd('SELECT *')
        self.assertTrue(exception_msg)


class CanMakeTables(unittest.TestCase):
    def test_one_table_making_remote(self):
        cmdr = cursors.Commander(connect_to_local_database=False)
        self.assertFalse(cmdr.tableset)
        cmdr.do_cmd(sql_command_library.read_db_creation_commands(test_directory)['person'])
        self.assertTrue(cmdr.tableset)
        self.assertIn('person', cmdr.tableset)





if __name__ == '__main__':
    unittest.main()
