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

import os

from cacher import Cacher
from runner import CommandRunner as runner
from util import *

def getAllBranches():
    """ Gets a list of all branches with the current branch at the end. """
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


def getCurrentBranch():
    return runner.get().run("git rev-parse --abbrev-ref HEAD")[:-1]


def getNextBranch():
    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nextBranch.txt")
    with open(filename, "r") as f:
        branch = f.read()
    branches = getAllBranches()
    for b in branches:
        if b == "head":
            continue
        if b >= branch:
            branch = getNextBranchNameFrom(b)

    nextBranch = getNextBranchNameFrom(branch)
    with open(filename, "w") as f:
        f.write(nextBranch)
    return branch


def getNextBranchNameFrom(branchName):
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    branchName = list(branchName)
    for i in range(len(branchName) - 1, -1, -1):
        if branchName[i] != "z":
            branchName[i] = alphabet[alphabet.find(branchName[i]) + 1]
            break
        branchName[i] = "a"
    return "".join(branchName)


def getCommitForBranch(reference: str) -> str:
    return runner.get().run(f"git rev-parse --short {reference}")[:-1]


def getUrlsForBranches():
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
    return runner.get().run(f"git show --no-patch --no-notes {reference} --format=%ce")[:-1] == runner.get().run("git config user.email")[:-1]

def rebaseBranches(queue, originalBranch):
    for i, branch in enumerate(queue):
        runner.get().run(f"git checkout {branch}")
        runner.get().runInProcess(f"git pull --rebase")
        if isRebaseInProgress():
            Cacher.cacheKey("REBASE_QUEUE", queue[i+1:])
            Cacher.cacheKey("ORIGINAL_REBASE_BRANCH", originalBranch)
            return
    Cacher.invalidateKey("REBASE_QUEUE")
    Cacher.invalidateKey("ORIGINAL_REBASE_BRANCH")
    runner.get().run(f"git checkout {originalBranch}")

def isRebaseInProgress() -> bool:
    return runner.get().run("git status").startswith("rebase in progress;")