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
from features import Features
from node import Node
from runner import CommandRunner as runner
from util import *


class Tree:
    _tree = None

    @classmethod
    def get(cls):
        if cls._tree:
            return cls._tree
        if not Features.SHOULD_CACHE_TREE:
            cls._tree = cls._generateTree()
            return cls._tree
        cachedHash = Cacher.getCachedKey(Cacher.TREE_HASH)
        currentHash = cls._getTreeHash()
        if currentHash == cachedHash:
            cls._tree = Cacher.getCachedKey(Cacher.TREE)
            return cls._tree

        Cacher.cacheKey(Cacher.TREE_HASH, currentHash)
        cls._tree = cls._generateTree()
        Cacher.cacheKey(Cacher.TREE, cls._tree)
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
        branchesToParents, parentsToBranches, uniqueHashes = cls._generateParentsAndBranches(
            branchNames)
        # Regenerate branch names as _generateParentsAndBranches may have 
        # created new branches.
        branchNames = branches.getAllBranches()
        for branch in branchNames:
            commit = branches.getCommitForBranch(branch)
            parent = branchesToParents[branch]
            children = parentsToBranches[branch]
            is_owned = branches.isBranchOwned(branch)
            tree[branch] = Node(branch, commit, parent, children, is_owned,
                                *uniqueHashes[commit])
        for branch in tree:
            tree[branch].parent = tree[
                tree[branch].parent] if tree[branch].parent else None
            tree[branch].children = [tree[i] for i in tree[branch].children]
        return tree

    @classmethod
    def _generateParentsAndBranches(cls, branchNames):
        # Set of commit hashes.
        commitSet = set()
        # List of tuples of (Commit Date, Commit Hash) sorted on Commit Date.
        unownedCommits = []
        # Maps commit hashes to branches.
        commitsToBranches = {}

        for branch in branchNames:
            commit = branches.getCommitForBranch(branch)
            commitSet.add(commit)
            assert commit not in commitsToBranches, (
                f"Two branches ({commitsToBranches[commit]} & {branch}) " +
                "point to the same commit. Please delete one of them.")
            commitsToBranches[commit] = branch
            if not branches.isBranchOwned(branch):
                bisect.insort(unownedCommits,
                              (commits.getDateForCommit(commit), commit))

        # Relates a parent branch to a set of child branches.
        parentsToBranches = defaultdict(set)
        # Relates a branch to its parent branch.
        branchesToParents = {}

        for branch in branchNames:
            if branch == "head":
                branchesToParents["head"] = None
                continue
            parent = branches.getCommitForBranch(f"{branch}^")
            if parent in commitSet:
                parentsToBranches[commitsToBranches[parent]].add(branch)
                branchesToParents[branch] = commitsToBranches[parent]
            # Orphan change
            elif branches.isBranchOwned(branch):
                # Create a new unowned branch for the new parent.
                newBranch = branches.createNewBranchAt(parent)
                commitSet.add(parent)
                parentDate = commits.getDateForCommit(parent)
                pos = bisect.bisect(unownedCommits, (parentDate, parent))
                skipParent = unownedCommits[pos - 1][1]

                if pos == len(unownedCommits):
                    unownedCommits.append(parent)
                else:
                    unownedCommits.insert(pos, (parentDate, parent))

                branchesToParents[branch] = newBranch
                branchesToParents[newBranch] = commitsToBranches[skipParent]
                parentsToBranches[newBranch].add(branch)
                parentsToBranches[commitsToBranches[skipParent]].add(newBranch)
            else:
                # This is an unowned node, we just want to insert it in the right place.
                parentDate = commits.getDateForCommit(parent)
                pos = bisect.bisect(unownedCommits, (parentDate, parent))
                parent = unownedCommits[pos - 1][1]
                parentsToBranches[commitsToBranches[parent]].add(branch)
                branchesToParents[branch] = commitsToBranches[parent]

        uniqueHashes = getUniqueCommitPrefixes(
            [branches.getCommitForBranch(b) for b in branchesToParents.keys()])
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
        nodesToDelete = []
        for branch in oldTree:
            if branch == "head":
                continue
            if not oldTree[branch].is_owned:
                if len([
                        child for child in oldTree[branch].children
                        if child.is_owned
                ]) == 0:
                    nodesToDelete.append(branch)
        for node in nodesToDelete:
            runner.get().run(f"git branch -D {node}")
        cls._tree = None
