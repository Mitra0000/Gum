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

import sys

import branches
from cacher import Cacher
import commits
from runner import CommandRunner as runner
from tree import Tree
from tree_printer import TreePrinter
from util import *

def parse(args):
    command = args[0]

    if command != "rebase" and (branches.isRebaseInProgress() or Cacher.getCachedKey("REBASE_QUEUE") is not None):
        return "Cannot perform tasks until current rebase is complete."

    if command == "add":
        if len(args) == 1:
            runner.get().runInProcess("git add -A")
        else:
            runner.get().runInProcess(f"git add {args[1]}")

    elif command == "amend":
        print("Amending changes.")
        originalBranch = branches.getCurrentBranch()
        allChildren = Tree.getRecursiveChildrenFrom(originalBranch)
        runner.get().run("git add -u")
        runner.get().run("git commit --amend --no-edit")
        print("Rebasing dependent branches.")
        branches.rebaseBranches(allChildren, originalBranch)
        return

    elif command == "commit":
        commitMessage = commits.createCommitMessage()
        if commitMessage is None:
            return None
        currentBranch = branches.getCurrentBranch()
        newBranch = branches.getNextBranch()
        if branches.isBranchOwned(currentBranch):
            # runner.get().run(f"git new-branch --upstream_current {newBranch}") # Only works on Chromium.
            runner.get().run(f"git checkout -b {newBranch}")
            runner.get().run(f"git branch --set-upstream-to={currentBranch}")
        else:
            # If we're currently on an unowned node we don't want to set an upstream so that we can upload to Gerrit.
            runner.get().run(f"git checkout -b {newBranch} {branches.getCommitForBranch(currentBranch)}")
            runner.get().run("git branch --set-upstream-to=origin/main")
        runner.get().run("git add -u")
        runner.get().runInProcess(f"git commit -m '{commitMessage}'")
        # Store the current branch name as x
        # Create a new branch called y
        # Set upstream of y to x
        # Add known changes to y
        # Commit with commitMessage to y

    elif command == "diff":
        runner.get().runInProcess("git diff")

    elif command == "fix":
        runner.get().runInProcess("git cl format")

    elif command == "init":
        runner.get().run("git branch -D head")
        runner.get().run("git checkout -b head")
        runner.get().run("git branch --set-upstream-to=origin/main head")
        for branch in branches.getAllBranches():
            if branch != "head":
                runner.get().run(f"git branch -D {branch}")
        runner.get().run("git pull --rebase")

    elif command == "patch":
        url = args[1]
        newbranch = branches.getNextBranch()
        runner.get().runInProcess(f"git cl patch -b {newbranch} {url}")

    elif command == "prune":
        if len(args) == 1:
            return "Please specify a hash to prune."
        commitHash = args[1]
        commit = commits.getCommitForPrefix(commitHash)
        if commit != None:
            commitHash = commit
        branchName = commits.getBranchForCommit(commitHash)
        if branchName is None:
            return "Could not find specified commit hash."
        runner.get().run(f"git branch -D {branchName}")

    elif command == "rebase":
        if len(args) == 2 and args[1] == "--continue":
            runner.get().runInProcess("git rebase --continue")
            if branches.isRebaseInProgress():
                return
            queue = Cacher.getCachedKey("REBASE_QUEUE")
            originalBranch = Cacher.getCachedKey("ORIGINAL_REBASE_BRANCH")
            if queue is not None:
                branches.rebaseBranches(queue, originalBranch)
            return
        if len(args) != 5:
            return "Please specify source and destination commit."
        sourceCommit = ""
        destinationCommit = ""
        if args[1] == "-s" and args[3] == "-d":
            sourceCommit = args[2]
            destinationCommit = args[4]
        elif args[1] == "-d" and args[3] == "-s":
            sourceCommit = args[4]
            destinationCommit = args[2]
        destinationCommit = commits.getCommitForPrefix(destinationCommit)
        sourceCommit = commits.getCommitForPrefix(sourceCommit)
        if sourceCommit == "" or destinationCommit == "":
            return
        sourceBranch = commits.getBranchForCommit(sourceCommit)
        destinationBranch = commits.getBranchForCommit(destinationCommit)
        runner.get().runInProcess(f"git rebase --onto {destinationCommit} {commits.getParentOfCommit(sourceCommit)} {sourceCommit}")
        runner.get().run(f"git checkout -B {sourceBranch} HEAD")
        if branches.isBranchOwned(destinationBranch):
            runner.get().run(f"git branch --set-upstream-to={destinationBranch} {sourceBranch}")
        else:
            runner.get().run(f"git branch --unset-upstream {sourceBranch}")
        updateHead()
        return

    elif command == "status":
        return getStatus()

    elif command == "sync":
        currentBranch = branches.getCurrentBranch()
        if not branches.isBranchOwned(currentBranch):
            return
        # Need to traverse and rebase all children.
        newBranch = branches.getNextBranch()
        runner.get().run("git checkout head")
        runner.get().run(f"git checkout -b {newBranch}")
        runner.get().run(f"git branch --set-upstream-to=origin/main {newBranch}")
        runner.get().run("git pull")

        # Move commit and children onto new branch.
        runner.get().run(f"git checkout {currentBranch}")
        runner.get().run(f"git rebase {newBranch}")

        updateHead()

    elif command == "test":
        return updateHead()

    elif command == "uncommit":
        tree = Tree.get()
        currentBranch = branches.getCurrentBranch()
        runner.get().run("git reset --soft HEAD^")
        runner.get().run(f"git checkout {tree[currentBranch].parent.branch}")
        runner.get().run(f"git branch -D {currentBranch}")

    elif command == "update":
        if len(args) == 1:
            return "Please specify a hash to update to."
        if getStatus() is not None:
            return "Cannot update with uncommitted changes.\nPlease commit/restore the changes and try again."
        commitHash = args[1]
        commit = commits.getCommitForPrefix(commitHash)
        if commit != None:
            commitHash = commit
        branchName = commits.getBranchForCommit(commitHash)
        if branchName is None:
            return "Could not find specified commit hash."
        runner.get().run(f"git checkout {branchName}")
        return f"Updated to {commitHash}"

    elif command == "uploadchain" or command == "uc":
        Cacher.invalidateKey(Cacher.CL_NUMBERS)
        originalRef = branches.getCurrentBranch()
        currentRef = originalRef
        commitStack = []
        while branches.isBranchOwned(currentRef):
            commitStack.append(currentRef)
            currentRef += "^"
        urls = []
        while commitStack:
            commitRef = commitStack.pop()
            commit = branches.getCommitForBranch(commitRef)
            branch = commits.getBranchForCommit(commit)
            runner.get().run(f"git checkout {branch}")
            runner.get().runInProcess("git cl upload -f")
            urls.append(commit)
        commitsToUrls = branches.getUrlsForBranches()
        print(f"Uploaded {len(urls)} CLs.")
        for commit in urls:
            if commit in commitsToUrls:
                print(commitsToUrls[commit], ":", runner.get().run(f"git log {commit} -1 --pretty=format:%s"))

    elif command == "uploadtree" or command == "ut":
        Cacher.invalidateKey(Cacher.CL_NUMBERS)
        runner.get().runInProcess("git cl upload -f --dependencies")

    elif command == "xl":
        tree = Tree.get()
        TreePrinter.print(tree["head"])

    else:
        return "Unknown gum command"


def updateHead():
    unownedBranches = []
    for child in Tree.get()["head"].children:
        if child.is_owned:
            return
    for branch in Tree.get():
        if not Tree.get()[branch].is_owned:
            unownedBranches.append(branch)
    
    unownedBranches = sorted(unownedBranches, key=commits.getDateForCommit)
    if len(unownedBranches) < 2:
        raise Exception("Update head called when head cannot be updated.")

    assert unownedBranches[0] == "head"

    newHead = unownedBranches[1]
    currentBranch = branches.getCurrentBranch()
    runner.get().run("git checkout head")
    runner.get().run(f"git pull origin {commits.getFullCommitHash(newHead)}")
    runner.get().run(f"git branch -D {newHead}") 
    runner.get().run(f"git checkout {currentBranch}")

def getStatus():
    status = runner.get().run("git status --porcelain")
    if status.strip() == "":
        return None
    out = []
    for line in status.split("\n"):
        if len(line) == 0:
            continue
        elif line[1] == "M":
            out.append(formatText("M" + line[2:], color = Color.Yellow))
        elif line[1] == "D":
            out.append(formatText("D" + line[2:], color = Color.Red))
        elif line[1] == "?":
            out.append(formatText("?" + line[2:], color = Color.Magenta))
        elif line[0] == "A":
            out.append(formatText("A" + line[2:], color = Color.Green))
    return "\n".join(out)  

def generateSwitches(arguments):
    switches = {}
    switches["command"] = arguments[0]
    lastKey = ""
    for arg in arguments[1:]:
        if arg.startswith("-"):
            lastKey = arg
            switches[arg] = True
        else:
            switches[lastKey] = arg
    return switches

if __name__ == '__main__':
    switches = generateSwitches(sys.argv[1:])
    result = parse(sys.argv[1:])
    if result is not None:
        print(result)
