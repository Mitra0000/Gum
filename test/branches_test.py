import unittest

from test_helper import TestHelper

# Unit tests for the BranchManager class.
class BranchManagerTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.helper = TestHelper()

    def setUp(self):
        self.helper.resetRepository()
        self.branchManager = self.helper.branchManager

    def testGetAllBranchesWithZeroBranches(self):
        self.helper.commandRunner.run("git branch -D head")
        self.assertEquals(self.branchManager.getAllBranches(), [])

    def testGetAllBranchesWithOneBranch(self):
        self.assertEquals(self.branchManager.getAllBranches(), ["head"])

    def testGetAllBranchesWithTwoBranches(self):
        self.helper.commandRunner.run("git checkout -b testBranch")
        self.assertEquals(self.branchManager.getAllBranches(), ["head", "testBranch"])

    def testGetAllBranchesHasCurrentBranchLast(self):
        self.helper.commandRunner.run("git checkout -b testBranch")
        self.assertEquals(self.branchManager.getAllBranches(), ["head", "testBranch"])
        self.helper.commandRunner.run("git checkout head")
        self.assertEquals(self.branchManager.getAllBranches(), ["testBranch", "head"])

    def testGetCurrentBranch(self):
        self.assertEquals(self.branchManager.getCurrentBranch(), "head")

    def testGetCurrentBranchWithMultipleBranches(self):
        self.helper.commandRunner.run("git checkout -b testBranch")
        self.assertEquals(self.branchManager.getCurrentBranch(), "testBranch")

    def testGetNextBranchName(self):
        testMethod = self.branchManager.getNextBranchNameFrom
        self.assertEquals(testMethod("aaaaa"), "aaaab")
        self.assertEquals(testMethod("aaaaz"), "aaaba")
        self.assertEquals(testMethod("abczd"), "abcze")
        self.assertEquals(testMethod("zzzzz"), "aaaaa")

    def testGetCommitForBranch(self):
        run = self.helper.commandRunner.run
        run("git checkout -b testBranch")
        self.helper.addChanges({("myfile.txt", "A"): "This is a new file."})
        run("git add -A")
        run("git commit -m 'This is a test'")
        self.assertEquals(self.branchManager.getCommitForBranch("testBranch"), self.helper.getHashForBranch("testBranch"))

    def testIsBranchOwnedWithHead(self):
        self.assertFalse(self.branchManager.isBranchOwned("head"))

    def testIsNewBranchOwnedWithoutCommit(self):
        self.helper.commandRunner.run("git checkout -b testBranch")
        self.assertFalse(self.branchManager.isBranchOwned("testBranch"))

    def testIsNewBranchOwnedWithCommit(self):
        run = self.helper.commandRunner.run
        run("git checkout -b testBranch")
        self.helper.addChanges({("myfile.txt", "A"): "This is a new file."})
        run("git add -A")
        run("git commit -m 'This is a test'")
        self.assertTrue(self.branchManager.isBranchOwned("testBranch"))


if __name__ == '__main__':
    unittest.main()