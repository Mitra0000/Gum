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

import commits

# Unit tests for the CommitManager class.
class CommitManagerTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.helper = TestHelper()
    
    def setUp(self):
        self.helper.resetRepository()
        self.repo = self.helper.repository

    def testGetBranchForCommit(self):
        self.assertEqual(commits.getBranchForCommit("0"), "head")

    def testGetSingleCommitForPrefix(self):
        commit = "123abc"
        self.repo.createNewBranch("test", commit)
        for i in range(1, len(commit) + 1):
            self.assertEqual(commits.getSingleCommitForPrefix(commit[0:i]), commit)

    def testGetSingleCommitForPrefixMultipleBranches(self):
        commit1 = "123abc"
        commit2 = "128cba"
        self.repo.createNewBranch("test1", commit1)
        self.repo.createNewBranch("test2", commit2)
        self.assertEqual(commits.getSingleCommitForPrefix("1"), None)
        self.assertEqual(commits.getSingleCommitForPrefix("12"), None)
        self.assertEqual(commits.getSingleCommitForPrefix("123"), commit1)
        self.assertEqual(commits.getSingleCommitForPrefix("128"), commit2)


if __name__ == '__main__':
    unittest.main()