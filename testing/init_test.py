import unittest

from integration import IntegrationTest

# Integration tests for the `gm init` command.
class InitTest(IntegrationTest):
    def testInitCommandOnEmptyRepository(self):
        self.runCommand(f"{self.GUM} init")
        branches = self.runCommand("git branch")
        self.assertEqual(branches, "* head\n")

if __name__ == '__main__':
    unittest.main()