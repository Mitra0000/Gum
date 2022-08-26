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

import bisect
from collections import defaultdict, deque

import branches
from cacher import Cacher
import commits
from node import Node
from runner import CommandRunner as runner
from util import *

class Tree:
    _tree = None

    @classmethod
    def get(cls):
        if cls._tree:
            return cls._tree
        tree = Cacher.getCachedKey(Cacher.TREE)
        if len(tree) == 0:
            return cls._generateTree()
        cachedHash = Cacher.getCachedKey(Cacher.TREE_HASH)
        currentHash = cls._getTreeHash()
        if currentHash == cachedHash:
            cls._tree = tree
            return cls._tree

        Cacher.cacheKey(Cacher.TREE_HASH, currentHash)
        tree = cls._generateTree()
        Cacher.cacheKey(Cacher.TREE, tree)
        cls._tree = tree
        return cls._tree
    
    @classmethod
    def getRecursiveChildrenFrom(cls, branch):
        tree = cls.get()
        if branch not in tree:
            raise Exception(f"Branch: {branch} not found")
        children = []
        frontier = deque()
        frontier.extend(tree[branch].children)
        while frontier:
            child = frontier.popleft()
            children.append(child.branch)
            frontier.extend(child.children)
        return children

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
    
    @classmethod
    def cleanup(cls):
        oldTree = cls.get()
        for branch in dict(oldTree):
            if branch == "head":
                continue
            if not oldTree[branch].is_owned:
                if len([child for child in oldTree[branch].children if child.is_owned]) == 0:
                    del oldTree[branch]
        cls._tree = None