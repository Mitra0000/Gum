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
        filename = "file_to_delete.txt"
        self.createFile(filename, "This file will be deleted.")
        self.runCommand("git add -A")
        self.runCommand("git commit -m 'Creates a file to delete.'")
        self.runCommand(f"rm {filename}")
        status = self.runCommand(f"{self.GUM} status")
        status = self.decodeFormattedText(status)
        self.assertEqual(status, f"D {filename}\n")

if __name__ == '__main__':
    unittest.main()