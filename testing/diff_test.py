import unittest

from integration import IntegrationTest

# Integration tests for the `gm diff` command.
class DiffTest(IntegrationTest):
    def testEmptyDiff(self):
        self.assertEqual(self.runCommand(f"{self.GUM} diff"), "")
        self.assertGumOutputEqualsGitOutput()

    def testAddedDiff(self):
        self.createFile("newfile.txt", "This is a new file.")
        self.assertGumOutputEqualsGitOutput()

    def testModifiedDiff(self):
        self.modifyFile("test.txt", "This is a modified test.")
        self.assertGumOutputEqualsGitOutput()

    def testDeletedDiff(self):
        self.modifyFile("test.txt", "")
        self.assertGumOutputEqualsGitOutput()

    def testMultiFileDiff(self):
        self.modifyFile("test.txt", "This is a modified test.")
        self.createFile("newfile.txt", "This is a new file.")
        self.assertGumOutputEqualsGitOutput()

    def assertGumOutputEqualsGitOutput(self):
        gumOutput = self.runCommand(f"{self.GUM} diff")
        gitOutput = self.runCommand("git diff")
        self.assertEqual(gumOutput, gitOutput)

if __name__ == '__main__':
    unittest.main()