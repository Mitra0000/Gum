from test_helper import TestHelper
from unittest import UnitTest, assertEquals

# Unit tests for the BranchManager class.
class BranchManagerTest(UnitTest):
    def setup(self):
        self.helper = TestHelper()

    def before(self):
        self.helper.resetRepository()
        self.branchManager = self.helper.branchManager

    @UnitTest.Test
    def testGetAllBranchesWithZeroBranches(self):
        self.helper.commandRunner.run("git branch -D head")
        assertEquals(self.branchManager.getAllBranches(), [])

    @UnitTest.Test
    def testGetAllBranchesWithOneBranch(self):
        assertEquals(self.branchManager.getAllBranches(), ["head"])

    @UnitTest.Test
    def testGetAllBranchesWithTwoBranches(self):
        self.helper.commandRunner.run("git checkout -b testBranch")
        assertEquals(self.branchManager.getAllBranches(), ["head", "testBranch"])

    @UnitTest.Test
    def testGetAllBranchesHasCurrentBranchLast(self):
        self.helper.commandRunner.run("git checkout -b testBranch")
        assertEquals(self.branchManager.getAllBranches(), ["head", "testBranch"])
        self.helper.commandRunner.run("git checkout head")
        assertEquals(self.branchManager.getAllBranches(), ["testBranch", "head"])

    @UnitTest.Test
    def testGetCurrentBranch(self):
        assertEquals(self.branchManager.getCurrentBranch(), "head")

    @UnitTest.Test
    def testGetCurrentBranchWithMultipleBranches(self):
        self.helper.commandRunner.run("git checkout -b testBranch")
        assertEquals(self.branchManager.getCurrentBranch(), "testBranch")

    @UnitTest.Test
    def testGetNextBranchName(self):
        assertEquals(self.branchManager.getNextBranchNameFrom("aaaaa"), "aaaab")
        assertEquals(self.branchManager.getNextBranchNameFrom("aaaaz"), "aaaba")
        assertEquals(self.branchManager.getNextBranchNameFrom("abczd"), "abcze")
        assertEquals(self.branchManager.getNextBranchNameFrom("zzzzz"), "aaaaa")

    def testGetCommitForBranch(self):
        run = self.helper.commandRunner.run
        run("git checkout -b testBranch")
        self.helper.addChanges({("myfile.txt", "A"): "This is a new file."})
        run("git add -A")