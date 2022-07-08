import bisect
from collections import defaultdict

import branches
from cacher import Cacher
import commits
from node import Node
from runner import CommandRunner as runner
from util import *

class Tree:
    @classmethod
    def get(cls):
        tree = Cacher.getCachedKey(Cacher.TREE)
        if len(tree) == 0:
            return cls._generateTree()
        cachedHash = Cacher.getCachedKey(Cacher.TREE_HASH)
        currentHash = cls._getTreeHash()
        if currentHash == cachedHash:
            return tree

        Cacher.cacheKey(Cacher.TREE_HASH, currentHash)
        tree = cls._generateTree()
        Cacher.cacheKey(Cacher.TREE, tree)
        return tree

    @classmethod
    def _generateTree(cls):
        branchNames = branches.getAllBranches()
        tree = {}
        branchesToParents, parentsToBranches, uniqueHashes = cls._generateParentsAndBranches(branchNames)
        for branch in branchNames:
            commit = branches.getCommitForBranch(branch)
            parent = branchesToParents[branch]
            children = parentsToBranches[branch]
            is_owned = branches.isBranchOwned(branch)
            tree[branch] = Node(branch, commit, parent, children, is_owned, *uniqueHashes[commit])
        for branch in tree:
            tree[branch].parent = tree[tree[branch].parent] if tree[branch].parent else None
            tree[branch].children = [tree[i] for i in tree[branch].children]
        return tree

    @classmethod
    def _generateParentsAndBranches(cls, branchNames):
        commitSet = set()
        unownedCommits = []
        parentsToBranches = defaultdict(set)
        branchesToParents = {}
        commitsToBranches = {}
        for branch in branchNames:
            commit = branches.getCommitForBranch(branch)
            commitSet.add(commit)
            commitsToBranches[commit] = branch
            if not branches.isBranchOwned(commit):
                bisect.insort(unownedCommits, (commits.getDateForCommit(commit), commit))

        for branch in branchNames:
            if branch == "head":
                branchesToParents["head"] = None
                continue
            parent = branches.getCommitForBranch(f"{branch}^")
            if parent not in commitSet:
                parentDate = commits.getDateForCommit(parent)
                for i in range(len(unownedCommits)):
                    if unownedCommits[i][0] > parentDate:
                        parent = unownedCommits[i - 1][1]
                        break
                else:
                    parent = unownedCommits[-1][1]
            parentsToBranches[commitsToBranches[parent]].add(branch)
            branchesToParents[branch] = commitsToBranches[parent]
        uniqueHashes = getUniqueCommitPrefixes([branches.getCommitForBranch(b) for b in branchesToParents.keys()])
        return branchesToParents, parentsToBranches, uniqueHashes 
    
    @classmethod
    def _getTreeHash(cls):
        totalHash = 0
        hashes = runner.get().run("git rev-parse --branches=*")
        for line in hashes.split("\n"):
            if line == "":
                continue
            totalHash += int(line, base=16)
        return hex(totalHash)[2:]