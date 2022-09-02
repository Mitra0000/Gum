"tmp", # Copyright 2022 The Gum Authors
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

import os

from cacher import Cacher
from runner import CommandRunner as runner
from util import *

def getAllBranches() -> "list[str]":
    """ Returns a list of all branches with the current branch at the end. """
    data = runner.get().run("git branch")
    data = data.split("\n")
    output = []
    current = ""
    for branch in data:
        if branch.startswith("*"):
            current = branch[2:]
            continue
        if branch == "":
            continue
        output.append(branch[2:])
    if current != "":
        output.append(current)
    return output


def getCurrentBranch() -> str:
    """ Returns the current branch name. """
    return runner.get().run("git rev-parse --abbrev-ref HEAD")[:-1]


def getNextBranch() -> str:
    """
        Returns the next unique branch name to use for creating a new branch. 
    """
    branch = Cacher.getCachedKey(Cacher.NEXT_BRANCH)
    branches = getAllBranches()
    # True when a branch exists with a name higher than the cached branch name.
    shouldIncrement = False

    for b in branches:
        if b == "head":
            continue
        if b >= branch:
            branch = b
            shouldIncrement = True

    if shouldIncrement:
        branch = getNextBranchNameFrom(branch)

    Cacher.cacheKey(Cacher.NEXT_BRANCH, getNextBranchNameFrom(branch))
    return branch


def getNextBranchNameFrom(branchName: str) -> str:
    """
        Takes a 5 character string and calculates the next alphabetical 
        5 character string.
    """
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    branchName = list(branchName)
    for i in range(len(branchName) - 1, -1, -1):
        if branchName[i] != "z":
            branchName[i] = alphabet[alphabet.find(branchName[i]) + 1]
            break
        branchName[i] = "a"
    return "".join(branchName)


def getCommitForBranch(reference: str) -> str:
    """
        Returns the short commit hash of a given branch/commit reference 
        (eg. HEAD^^). 
    """
    return runner.get().run(f"git rev-parse --short {reference}")[:-1]


def getUrlsForBranches() -> "dict[str, str]":
    """
        Returns a dictionary mapping branch names to their CL URLs if they 
        exist.
    """
    branchesToUrls = {}
    output = runner.get().run("git cl status -f --no-branch-color")
    output = output.split("\n")[1:]
    for i in range(len(output)):
        if output[i] == "":
            break

        data = output[i].strip()
        if data.startswith("*"):
            data = data[2:]
        data = data.split()
        branchesToUrls[getCommitForBranch(data[0])] = data[2]
    Cacher.cacheKey(Cacher.CL_NUMBERS, branchesToUrls)
    return branchesToUrls

def isBranchOwned(reference: str) -> str:
    """ Returns whether the commit was authored by the current Git user. """
    return runner.get().run(f"git show --no-patch --no-notes {reference} --format=%ce")[:-1] == runner.get().run("git config user.email")[:-1]

def rebaseBranches(queue: "list[str]", originalBranch: str) -> None:
    """
        Iterates through a queue of branches, rebasing each onto its 
        upstream parent.
    """
    for i, branch in enumerate(queue):
        runner.get().run(f"git checkout {branch}", True)
        runner.get().runInProcess(f"git pull --rebase")
        if isRebaseInProgress():
            Cacher.cacheKey("REBASE_QUEUE", queue[i+1:])
            Cacher.cacheKey("ORIGINAL_REBASE_BRANCH", originalBranch)
            return
    Cacher.invalidateKey("REBASE_QUEUE")
    Cacher.invalidateKey("ORIGINAL_REBASE_BRANCH")
    runner.get().run(f"git checkout {originalBranch}", True)

def isRebaseInProgress() -> bool:
    """ Returns true if a rebase is currently in progress. """
    return runner.get().run("git status").startswith("rebase in progress;")