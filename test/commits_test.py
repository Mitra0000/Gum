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
from node import Node

# Unit tests for the CommitManager class.
class CommitManagerTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.helper = TestHelper()
    
    def setUp(self):
        self.helper.resetRepository()

    def testBuildTreeWithOneCommit(self):
        commitHashes = set()
        commitHashes.add("head")
        tree = commits.buildTreeFromCommits({}, commitHashes)
        self.assertEquals(tree.children, [])
        self.assertIsInstance(tree, Node)
        self.assertEquals(tree.commitHash, "head")
    
    def testBulidTreeWithTwoCommits(self):
        self.helper.repository.commitTree.createBranch("123", "head")
        commitHashes = set(["123", "head"])
        parentsToCommits = {"head": ["123"]}
        root = commits.buildTreeFromCommits(parentsToCommits, commitHashes)
        self.assertEquals(len(root.children), 1)
        self.assertEquals(root.commitHash, "head")
        self.assertEquals(root.children[0].commitHash, "123")
    
    def testBuildTreeWithMultipleChildren(self):
        self.helper.repository.commitTree.createBranch("123", "head")
        self.helper.repository.commitTree.createBranch("456", "head")
        commitHashes = set(["123", "456", "head"])
        parentsToCommits = {"head": ["123", "456"]}
        root = commits.buildTreeFromCommits(parentsToCommits, commitHashes)
        self.assertEquals(len(root.children), 2)
        self.assertEquals(root.commitHash, "head")
        self.assertTrue("123" in [x.commitHash for x in root.children])
        self.assertTrue("456" in [x.commitHash for x in root.children])

    def testBuildTreeWithDisjointedTree(self):
        self.helper.repository.commitTree.createBranch("123", "head")
        self.helper.repository.commitTree.createDetachedBranch("unjoined")
        commitHashes = set(["123", "unjoined", "head"])
        parentsToCommits = {"head": ["123"]}
        root = commits.buildTreeFromCommits(parentsToCommits, commitHashes)
        self.assertEquals(len(root.children), 2)
        self.assertEquals(root.commitHash, "head")
        self.assertTrue("123" in [x.commitHash for x in root.children])
        self.assertTrue("unjoined" in [x.commitHash for x in root.children])
    
    def testGetBranchForCommit(self):
        self.assertEquals(commits.getBranchForCommit("aaaaa"), "head")