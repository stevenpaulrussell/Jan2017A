import unittest

import dataqueda_constants
import action


class MyTestCaseDrivesFirstRunThroughSimply(unittest.TestCase):
    """
    Adding a spreadsheet to a directory results in an action detecting the addition, finding the right table for
    data insertion, finding the conditions to commit the insertion and what to do about 'mirroring', doing the
    insertion (presume no errors for now), and reporting the results.

    Need to specify the directories, how they chain, how they instruct
    """

    # move a test file into new_imports_whole/person
    def setUp(self):
        self.tableset = action.get_current_tableset(connect=dataqueda_constants.LOCAL)


    def test_poll_for_changes_returns_directories_having_changes(self):
        result = action.get_current_tableset(connect=dataqueda_constants.LOCAL)
        self.assertIn('person', result)
        print(result)



if __name__ == '__main__':
    unittest.main()
