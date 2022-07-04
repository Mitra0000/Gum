import os
import unittest

from integration import IntegrationTest

# Integration tests for the `gm init` command.
class InitTest(IntegrationTest):
    def testInitCommandOnEmptyRepository(self):
        self.createFirstCommit()
        branches = self.runCommand("git branch")
        self.assertEqual(branches, "* head\n")
    
    def testInitCommandOnRepositoryWithBranches(self):
        self.createFirstCommit()
        self.runCommand("git checkout -b testBranch")
        self.runCommand("git checkout -b otherBranch")
        self.createFile("newfile.txt", "This is a new file.")
        self.runCommand("git add -A")
        self.runCommand("git commit -m 'Second_commit'")
        self.runCommand(f"{self.GUM} init")
        branches = self.runCommand("git branch")
        self.assertEqual(branches, "* head\n")

if __name__ == '__main__':
    unittest.main()