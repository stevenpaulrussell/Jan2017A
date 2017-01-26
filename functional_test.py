import unittest


class MyTestCaseDrivesFirstRunThroughSimply(unittest.TestCase):
    """
    Adding a spreadsheet to a directory results in an action detecting the addition, finding the right table for
    data insertion, finding the conditions to commit the insertion and what to do about 'mirroring', doing the
    insertion (presume no errors for now), and reporting the results.

    Need to specify the directories, how they chain, how they instruct

    """
    def test_something(self):
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
