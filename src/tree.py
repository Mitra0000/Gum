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
from config.cacher import Cacher
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
            # TODO: Add check for empty commit
            tree[branch] = Node(branch, commit, parent, children, is_owned,
                                *uniqueHashes[commit])
        for branch in tree:
            tree[branch].parent = tree[
                tree[branch].parent] if tree[branch].parent else None
            tree[branch].children = [tree[i] for i in tree[branch].children]
        return tree

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

    @classmethod
    def _generateParentsAndBranches(cls, branchNames):
        """
            Generates mappings to be used to generate the tree object.
            This is split into a few distinct stages.
                1.) Create bi directional mappings between commits and branches.
                    Also create a list of unowned commits in date order.
                    There is a check at this stage to ensure that no two 
                    branches point to the same commit.
                
                2.) Iterate through the branches and map each branch's commit 
                    to its parent and its children. These mappings are stored in 
                    commitsToParents and parentsToCommits respectively.
                    This stage also realises phantom nodes. Nodes whose parents 
                    are not pointed to by a branch have "phantom" parents. They 
                    exist but not in Gum's commit tree. Branches are created for 
                    each of these phantom parents in this stage.
                
                3.) If an unowned commit has a commit date before the head 
                    branch, the names of the branches are swapped. The new head 
                    branch will be the oldest unowned commit in the repository.

                4.) Branchify the mappings: the two dictionaries containing the 
                    commit mappings are copied but each commit reference is 
                    replaced with a branch name.
        """
        # Set of commit hashes.
        commitSet = set()
        # List of tuples of (Commit Date, Commit Hash) sorted on Commit Date.
        unownedCommits = []
        # Maps commit hashes to branches.
        commitsToBranches = {}
        # Maps branches to commit hashes.
        branchesToCommits = {}

        for branch in branchNames:
            commit = branches.getCommitForBranch(branch)
            commitSet.add(commit)
            assert commit not in commitsToBranches, (
                f"Two branches ({commitsToBranches[commit]} & {branch}) " +
                "point to the same commit. Please delete one of them.")
            commitsToBranches[commit] = branch
            branchesToCommits[branch] = commit
            if not branches.isBranchOwned(branch):
                bisect.insort(unownedCommits,
                              (commits.getDateForCommit(commit), commit))

        # Relates a parent commit to a set of child commits.
        parentsToCommits = defaultdict(set)
        # Relates a commit to its parent commit.
        commitsToParents = {}

        for branch in branchNames:
            if branch == "head":
                commitsToParents[branchesToCommits["head"]] = None
                continue
            commit = branchesToCommits[branch]
            parent = branches.getCommitForBranch(f"{branch}^")
            if parent in commitSet:
                parentsToCommits[parent].add(commit)
                commitsToParents[commit] = parent
            # Orphan change
            elif branches.isBranchOwned(branch):
                # Create a new unowned branch for the new parent.
                newBranch = branches.createNewBranchAt(parent)
                commitsToBranches[parent] = newBranch
                branchesToCommits[newBranch] = commit
                commitSet.add(parent)
                parentDate = commits.getDateForCommit(parent)
                pos = bisect.bisect(unownedCommits, (parentDate, parent))
                skipParent = unownedCommits[pos - 1][1]

                if pos == len(unownedCommits):
                    unownedCommits.append(parent)
                else:
                    unownedCommits.insert(pos, (parentDate, parent))

                commitsToParents[commit] = parent
                commitsToParents[parent] = skipParent
                parentsToCommits[parent].add(commit)
                parentsToCommits[skipParent].add(parent)
            else:
                # This is an unowned node, we just want to insert it in the
                # right place.
                parentDate = commits.getDateForCommit(parent)
                pos = bisect.bisect(unownedCommits, (parentDate, parent))
                parent = unownedCommits[pos - 1][1]
                parentsToCommits[parent].add(commit)
                commitsToParents[commit] = parent

        # Need to move this to be after dealing with orphans.
        if commitsToBranches[unownedCommits[0][1]] != "head":
            # Head is not the oldest unowned commit.
            branchToSwap = commitsToBranches[unownedCommits[0][1]]
            headCommit = branches.getCommitForBranch("head")
            # Swap the name of the two branches.
            runner.get().run("git branch -m head head-temp")
            runner.get().run(f"git branch -m {branchToSwap} head")
            runner.get().run(f"git branch -m head-temp {branchToSwap}")
            commitsToBranches[headCommit], commitsToBranches[
                unownedCommits[0][1]] = commitsToBranches[
                    unownedCommits[0][1]], commitsToBranches[headCommit]
            commitsToParents[unownedCommits[0][1]] = None
            commitsToParents[headCommit] = unownedCommits[0][1]
            parentsToCommits[unownedCommits[0][1]].add(headCommit)
            parentsToCommits[headCommit].remove(unownedCommits[0][1])

        # Relates a parent commit to a set of child commits.
        parentsToBranches = defaultdict(set)
        # Relates a commit to its parent commit.
        branchesToParents = {}

        # It's important to "branchify" the dictionaries at this stage as some
        # branches may have switched names (and therefore switched the commits
        # they point to however each commit still points to the same
        # parent/child commits).
        #
        # This code simply copies the two dictionaries before but turns every
        # commit reference into a branch name.
        for entry in parentsToCommits:
            parentsToBranches[commitsToBranches[entry]] = {
                commitsToBranches[item] for item in parentsToCommits[entry]
            }
        for entry in commitsToParents:
            branchesToParents[commitsToBranches[entry]] = commitsToBranches[
                commitsToParents[entry]] if commitsToParents[entry] else None

        uniqueHashes = getUniqueCommitPrefixes(commitsToParents.keys())
        return branchesToParents, parentsToBranches, uniqueHashes
