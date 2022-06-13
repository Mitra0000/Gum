import unittest

from test_helper import TestHelper

from branches import Node

# Unit tests for the CommitManager class.
class CommitManagerTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.helper = TestHelper()
        self.commitManager = self.helper.commitManager
    
    def setUp(self):
        self.helper.resetRepository()

    def testBuildTreeWithOneCommit(self):
        commits = set()
        commits.add("head")
        tree = self.commitManager.buildTreeFromCommits({}, commits)
        self.assertEquals(tree.children, [])
        self.assertIsInstance(tree, Node)
        self.assertEquals(tree.commitHash, "head")
    
    def testBulidTreeWithTwoCommits(self):
        self.helper.repository.commitTree.createBranch("123", "head")
        commits = set(["123", "head"])
        parentsToCommits = {"head": ["123"]}
        root = self.commitManager.buildTreeFromCommits(parentsToCommits, commits)
        self.assertEquals(len(root.children), 1)
        self.assertEquals(root.commitHash, "head")
        self.assertEquals(root.children[0].commitHash, "123")
    
    def testBuildTreeWithMultipleChildren(self):
        self.helper.repository.commitTree.createBranch("123", "head")
        self.helper.repository.commitTree.createBranch("456", "head")
        commits = set(["123", "456", "head"])
        parentsToCommits = {"head": ["123", "456"]}
        root = self.commitManager.buildTreeFromCommits(parentsToCommits, commits)
        self.assertEquals(len(root.children), 2)
        self.assertEquals(root.commitHash, "head")
        self.assertTrue("123" in [x.commitHash for x in root.children])
        self.assertTrue("456" in [x.commitHash for x in root.children])

    def testBuildTreeWithDisjointedTree(self):
        self.helper.repository.commitTree.createBranch("123", "head")
        self.helper.repository.commitTree.createDetachedBranch("unjoined")
        commits = set(["123", "unjoined", "head"])
        parentsToCommits = {"head": ["123"]}
        root = self.commitManager.buildTreeFromCommits(parentsToCommits, commits)
        self.assertEquals(len(root.children), 2)
        self.assertEquals(root.commitHash, "head")
        self.assertTrue("123" in [x.commitHash for x in root.children])
        self.assertTrue("unjoined" in [x.commitHash for x in root.children])
    
    def testGetBranchForCommit(self):
        self.assertEquals(self.commitManager.getBranchForCommit("aaaaa"), "head")