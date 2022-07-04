import unittest

from integration import IntegrationTest

# Integration tests for the `gm status` command.
class StatusTest(IntegrationTest):
    def testEmptyStatusShowsNothing(self):
        status = self.runCommand(f"{self.GUM} status")
        self.assertEqual(status, "")

    def testNewFileShowsUntracked(self):
        self.createFirstCommit()
        filename = "untracked_file.txt"
        self.createFile(filename, "This is an untracked file.")
        status = self.runCommand(f"{self.GUM} status")
        status = self.decodeFormattedText(status)
        self.assertEqual(status, f"? {filename}\n")
    
    def testAddedFileShowsAdded(self):
        self.createFirstCommit()
        filename = "added_file.txt"
        self.createFile(filename, "This is an added file.")
        self.runCommand("git add -A")
        status = self.runCommand(f"{self.GUM} status")
        status = self.decodeFormattedText(status)
        self.assertEqual(status, f"A {filename}\n")
    
    def testDeletedFileShowsDeleted(self):
        self.createFirstCommit()
        filename = "test.txt"
        self.runCommand(f"rm {filename}")
        status = self.runCommand(f"{self.GUM} status")
        status = self.decodeFormattedText(status)
        self.assertEqual(status, f"D {filename}\n")
    
    def testModifiedFileShowsModified(self):
        self.createFirstCommit()
        filename = "test.txt"
        self.modifyFile(filename, "This file has been modified.")
        status = self.runCommand(f"{self.GUM} status")
        status = self.decodeFormattedText(status)
        self.assertEqual(status, f"M {filename}\n")
    
    def testMultipleStatuses(self):
        self.createFirstCommit()
        self.createFile("added_file.txt", "This is an added file.")
        self.runCommand("rm test.txt")
        status = self.runCommand(f"{self.GUM} status")
        status = self.decodeFormattedText(status)
        self.assertEqual(status, "D test.txt\n? added_file.txt\n")


if __name__ == '__main__':
    unittest.main()