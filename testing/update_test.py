import unittest

from integration import IntegrationTest

# Integration tests for the `gm update` command.
class UpdateTest(IntegrationTest):
    def testUpdateSwitchesBetweenCommits(self):
        self.assertEqual(self.runCommand("git rev-parse --abbrev-ref HEAD"), "head\n")

        # Create two commit branches: foo and bar.
        self.runCommand("git checkout -b foo")
        self.createFile("foo.txt", "foo")
        self.runCommand("git commit -m 'foo'")
        foo_hash = self.runCommand("git rev-parse HEAD")
        self.runCommand("git checkout -b bar")
        self.createFile("bar.txt", "bar")
        self.runCommand("git commit -m 'bar'")
        bar_hash = self.runCommand("git rev-parse HEAD")
        self.runCommand("git checkout head")

        self.runCommand(f"{self.GUM} update {foo_hash}")
        self.assertEqual(self.runCommand("git rev-parse HEAD"), foo_hash)
        self.runCommand(f"{self.GUM} update {bar_hash}")
        self.assertEqual(self.runCommand("git rev-parse HEAD"), bar_hash)

    def testWontUpdateWithUncommittedChanges(self):
        self.runCommand("git checkout -b foo")
        self.createFile("foo.txt", "foo")
        self.runCommand("git commit -m 'foo'")
        foo_hash = self.runCommand("git rev-parse HEAD")
        self.createFile("bar.txt", "bar")
        self.runCommand(f"{self.GUM} update head")
        self.assertEqual(self.runCommand("git rev-parse HEAD"), foo_hash)

if __name__ == '__main__':
    unittest.main()