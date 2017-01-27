import unittest


class MyTestCaseDrivesFirstRunThroughSimply(unittest.TestCase):
    """
    Adding a spreadsheet to a directory results in an action detecting the addition, finding the right table for
    data insertion, finding the conditions to commit the insertion and what to do about 'mirroring', doing the
    insertion (presume no errors for now), and reporting the results.

    Putting a file into the new_imports_whole/person folder results in that file being imported into the person table
    if there are no errors.  If no errors were found, the file is moved from imports_whole/person to mirrors/person.
    If there are errors, the file is removed from person and put into error_files with the errors shown per line.

    Need to specify the directories, how they chain, how they instruct



    """
    def test_something(self):
        # move a test file into new_imports_whole/person
        # call action to poll for changes
        # call action to run the found change
        # have different tests for case file has errors, has no errors.
        # don't forget to initialize and clean up.
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
