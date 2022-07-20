import unittest

from integration import IntegrationTest

# Integration tests for the `gm add` command.
class AddTest(IntegrationTest):
    def testAddCommandTracksUntrackedFile(self):
        self.createFirstCommit()
        self.createFile("added_file.txt", "This was just added.")
        status = self.runCommand("git status --porcelain")
        self.assertEqual(status, "?? added_file.txt\n")
        self.runCommand(f"{self.GUM} add")
        status = self.runCommand("git status --porcelain")
        self.assertEqual(status, "A  added_file.txt\n")
    
    def testAddSpecificFileDoesntAddAllFiles(self):
        self.createFirstCommit()
        self.createFile("foo.txt", "This is foo.")
        self.createFile("bar.txt", "This is bar.")
        status = self.runCommand("git status --porcelain")
        self.assertEqual(status, "?? bar.txt\n?? foo.txt\n")
        self.runCommand(f"{self.GUM} add foo.txt")
        status = self.runCommand("git status --porcelain")
        self.assertEqual(status, "A  foo.txt\n?? bar.txt\n")

if __name__ == '__main__':
    unittest.main()