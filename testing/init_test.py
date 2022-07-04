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
        with open(os.path.join(self.TEST_REPOSITORY, "newfile.txt"), "w") as f:
            f.write("This is a new file.")
        self.runCommand("git add -A")
        self.runCommand("git commit -m 'Second_commit'")
        self.runCommand(f"{self.GUM} init")
        branches = self.runCommand("git branch")
        self.assertEqual(branches, "* head\n")
    
    def createFirstCommit(self):
        self.runCommand(f"{self.GUM} init")
        with open(os.path.join(self.TEST_REPOSITORY, "test.txt"), "w") as f:
            f.write("This is a test.")
        self.runCommand("git add -A")
        self.runCommand("git commit -m 'Initial_commit.'")

if __name__ == '__main__':
    unittest.main()