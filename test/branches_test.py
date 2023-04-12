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
from cacher_for_testing import CacherForTesting
from test_helper import TestHelper

import branches
from config.cacher import Cacher


# Unit tests for the functions found in src/branches.py.
class BranchesTest(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.helper = TestHelper()

    def setUp(self):
        self.helper.resetRepository()
        self.repo = self.helper.repository

    # Tests for getAllBranches.
    def testGetAllBranchesWithZeroBranches(self):
        self.repo.removeBranch("head")
        self.assertEqual([], branches.getAllBranches())

    def testGetAllBranchesWithOneBranch(self):
        self.assertEqual(["head"], branches.getAllBranches())

    def testGetAllBranchesWithTwoBranches(self):
        self.repo.createNewBranch("testBranch")
        self.repo.setCurrentBranch("testBranch")
        self.assertEqual(["head", "testBranch"], branches.getAllBranches())

    def testGetAllBranchesHasCurrentBranchLast(self):
        self.repo.createNewBranch("testBranch")
        self.repo.setCurrentBranch("head")
        self.assertEqual(["testBranch", "head"], branches.getAllBranches())

    # Tests for getCurrentBranch.
    def testGetCurrentBranch(self):
        self.assertEqual(branches.getCurrentBranch(), "head")

    def testGetCurrentBranchWithMultipleBranches(self):
        self.repo.createNewBranch("testBranch")
        self.repo.setCurrentBranch("testBranch")
        self.assertEqual("testBranch", branches.getCurrentBranch())

    # Tests for getNextBranch.
    def testGetNextBranch(self):
        Cacher.swapInstanceForTesting(CacherForTesting())
        Cacher.cacheKey(Cacher.NEXT_BRANCH, "aaaac")
        self.assertEqual("aaaac", branches.getNextBranch())

    def testGetNextBranchWithHigherBranch(self):
        Cacher.swapInstanceForTesting(CacherForTesting())
        self.repo.createNewBranch("abcde")
        Cacher.cacheKey(Cacher.NEXT_BRANCH, "abbab")
        self.assertEqual("abcdf", branches.getNextBranch())

    def testGetNextBranchWithEqualBranch(self):
        Cacher.swapInstanceForTesting(CacherForTesting())
        self.repo.createNewBranch("abbab")
        Cacher.cacheKey(Cacher.NEXT_BRANCH, "abbab")
        self.assertEqual("abbac", branches.getNextBranch())

    # Tests for getNextBranchNameFrom.
    def testGetNextBranchName(self):
        self.assertEqual("aaaab", branches.getNextBranchNameFrom("aaaaa"))
        self.assertEqual("aaaba", branches.getNextBranchNameFrom("aaaaz"))
        self.assertEqual("abcze", branches.getNextBranchNameFrom("abczd"))
        self.assertEqual("aaaaa", branches.getNextBranchNameFrom("zzzzz"))

    # Tests for getCommitForBranch.
    def testGetCommitForBranch(self):
        self.repo.createNewBranch("testBranch")
        self.assertEqual("1", branches.getCommitForBranch("testBranch"))

    # Tests for isBranchOwned
    def testIsBranchOwnedWithHead(self):
        self.assertFalse(branches.isBranchOwned("head"))

    def testIsNewBranchOwned(self):
        self.repo.createNewBranch("testBranch")
        self.assertTrue(branches.isBranchOwned("testBranch"))

    def testIsUnownedBranchOwned(self):
        self.repo.createNewBranch("testBranch")
        self.repo.tree["testBranch"].is_owned = False
        self.assertFalse(branches.isBranchOwned("testBranch"))


if __name__ == '__main__':
    unittest.main()
