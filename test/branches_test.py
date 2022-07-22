# Copyright 2022 The Gum Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest

import context
from test_helper import TestHelper

import branches

# Unit tests for the BranchManager class.
class BranchManagerTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.helper = TestHelper()

    def setUp(self):
        self.helper.resetRepository()

    def testGetAllBranchesWithZeroBranches(self):
        self.helper.commandRunner.run("git branch -D head")
        self.assertEquals(branches.getAllBranches(), [])

    def testGetAllBranchesWithOneBranch(self):
        self.assertEquals(branches.getAllBranches(), ["head"])

    def testGetAllBranchesWithTwoBranches(self):
        self.helper.commandRunner.run("git checkout -b testBranch")
        self.assertEquals(branches.getAllBranches(), ["head", "testBranch"])

    def testGetAllBranchesHasCurrentBranchLast(self):
        self.helper.commandRunner.run("git checkout -b testBranch")
        self.assertEquals(branches.getAllBranches(), ["head", "testBranch"])
        self.helper.commandRunner.run("git checkout head")
        self.assertEquals(branches.getAllBranches(), ["testBranch", "head"])

    def testGetCurrentBranch(self):
        self.assertEquals(branches.getCurrentBranch(), "head")

    def testGetCurrentBranchWithMultipleBranches(self):
        self.helper.commandRunner.run("git checkout -b testBranch")
        self.assertEquals(branches.getCurrentBranch(), "testBranch")

    def testGetNextBranchName(self):
        testMethod = branches.getNextBranchNameFrom
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
        self.assertEquals(branches.getCommitForBranch("testBranch"), self.helper.getHashForBranch("testBranch"))

    def testIsBranchOwnedWithHead(self):
        self.assertFalse(branches.isBranchOwned("head"))

    def testIsNewBranchOwnedWithoutCommit(self):
        self.helper.commandRunner.run("git checkout -b testBranch")
        self.assertFalse(branches.isBranchOwned("testBranch"))

    def testIsNewBranchOwnedWithCommit(self):
        run = self.helper.commandRunner.run
        run("git checkout -b testBranch")
        self.helper.addChanges({("myfile.txt", "A"): "This is a new file."})
        run("git add -A")
        run("git commit -m 'This is a test'")
        self.assertTrue(branches.isBranchOwned("testBranch"))


if __name__ == '__main__':
    unittest.main()