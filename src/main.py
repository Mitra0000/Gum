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

import branches
from cacher import Cacher
import commits
import parser
from runner import CommandRunner as runner
from runner import DryRunner
from runner import VerboseRunner
from tree import Tree
from tree_printer import TreePrinter
from util import *

def main(args):
    command = args.command

    if command != "continue" and (branches.isRebaseInProgress() or Cacher.getCachedKey("REBASE_QUEUE") is not None):
        return "Cannot perform tasks until current rebase is complete. \nPlease resolve conflicts and then run `gm continue`."

    if args.verbose:
        runner.swapInstance(VerboseRunner())
    if args.dry_run:
        runner.swapInstance(DryRunner())

    if command == "add":
        # Flatten the parsed filenames.
        files = [item for inner in args.files for item in inner]
        if len(files) == 0:
            runner.get().runInProcess("git add -A")
        else:
            runner.get().runInProcess(f"git add {' '.join(files)}")

    elif command == "amend":
        print("Amending changes.")
        originalBranch = branches.getCurrentBranch()
        allChildren = Tree.getRecursiveChildrenFrom(originalBranch)
        runner.get().run("git add -u", True)
        runner.get().run("git commit --amend --no-edit", True)
        print("Rebasing dependent branches.")
        branches.rebaseBranches(allChildren, originalBranch)
        return

    elif command == "commit":
        commitMessage = commits.createCommitMessage()
        if commitMessage is None:
            return "Commit cancelled."
        currentBranch = branches.getCurrentBranch()
        newBranch = branches.getNextBranch()
        if branches.isBranchOwned(currentBranch):
            # runner.get().run(f"git new-branch --upstream_current {newBranch}") # Only works on Chromium.
            runner.get().run(f"git checkout -b {newBranch}", True)
            runner.get().run(f"git branch --set-upstream-to={currentBranch}", True)
        else:
            # If we're currently on an unowned node we don't want to set an upstream so that we can upload to Gerrit.
            runner.get().run(f"git checkout -b {newBranch} {branches.getCommitForBranch(currentBranch)}", True)
            runner.get().run("git branch --set-upstream-to=origin/main", True)
        runner.get().run("git add -u", True)
        runner.get().runInProcess(f"git commit -m '{commitMessage}'")
        # Store the current branch name as x
        # Create a new branch called y
        # Set upstream of y to x
        # Add known changes to y
        # Commit with commitMessage to y
    
    elif command == "continue":
        runner.get().runInProcess("git rebase --continue")
        if branches.isRebaseInProgress():
            return
        queue = Cacher.getCachedKey("REBASE_QUEUE")
        originalBranch = Cacher.getCachedKey("ORIGINAL_REBASE_BRANCH")
        if queue is not None:
            branches.rebaseBranches(queue, originalBranch)
        return

    elif command == "diff":
        runner.get().runInProcess("git diff")

    elif command == "fix":
        runner.get().runInProcess("git cl format")

    elif command == "init":
        runner.get().run("git branch -D head", True)
        runner.get().run("git checkout -b head", True)
        runner.get().run("git branch --set-upstream-to=origin/main head", True)
        for branch in branches.getAllBranches():
            if branch != "head":
                runner.get().run(f"git branch -D {branch}", True)
        runner.get().run("git pull --rebase", True)

    elif command == "patch":
        newbranch = branches.getNextBranch()
        runner.get().runInProcess(f"git cl patch -b {newbranch} {args.cl} {'--force' if not args.copy else ''}")

    elif command == "prune":
        commit = commits.getCommitForPrefix(args.commit)
        if commit != None:
            args.commit = commit
        branchName = commits.getBranchForCommit(args.commit)
        if branchName is None:
            return "Could not find specified commit hash."
        runner.get().run(f"git branch -D {branchName}", True)

    elif command == "rebase":
        destinationCommit = commits.getCommitForPrefix(args.destination)
        sourceCommit = commits.getCommitForPrefix(args.source)
        if sourceCommit == "" or destinationCommit == "":
            return f"Could not find specified commit: {args.source if sourceCommit == '' else args.destination}"
        sourceBranch = commits.getBranchForCommit(sourceCommit)
        destinationBranch = commits.getBranchForCommit(destinationCommit)
        runner.get().runInProcess(f"git rebase --onto {destinationCommit} {commits.getParentOfCommit(sourceCommit)} {sourceCommit}")
        runner.get().run(f"git checkout -B {sourceBranch} HEAD", True)
        if branches.isBranchOwned(destinationBranch):
            runner.get().run(f"git branch --set-upstream-to={destinationBranch} {sourceBranch}", True)
        else:
            runner.get().run(f"git branch --unset-upstream {sourceBranch}", True)
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
        runner.get().run("git checkout head", True)
        runner.get().run(f"git checkout -b {newBranch}", True)
        runner.get().run(f"git branch --set-upstream-to=origin/main {newBranch}", True)
        runner.get().run("git pull", True)

        # Move commit and children onto new branch.
        runner.get().run(f"git checkout {currentBranch}", True)
        runner.get().run(f"git rebase {newBranch}", True)

        updateHead()

    elif command == "test":
        return args

    elif command == "uncommit":
        tree = Tree.get()
        currentBranch = branches.getCurrentBranch()
        runner.get().run("git reset --soft HEAD^", True)
        runner.get().run(f"git checkout {tree[currentBranch].parent.branch}", True)
        runner.get().run(f"git branch -D {currentBranch}", True)

    elif command == "update":
        if getStatus() is not None:
            return "Cannot update with uncommitted changes.\nPlease commit/restore the changes and try again."
        commit = commits.getCommitForPrefix(args.commit)
        if commit != None:
            args.commit = commit
        branchName = commits.getBranchForCommit(args.commit)
        if branchName is None:
            return "Could not find specified commit hash."
        runner.get().run(f"git checkout {branchName}", True)
        return f"Updated to {args.commit}"

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
            runner.get().run(f"git checkout {branch}", True)
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
    runner.get().run("git checkout head", True)
    runner.get().run(f"git pull origin {commits.getFullCommitHash(newHead)}", True)
    runner.get().run(f"git branch -D {newHead}", True) 
    runner.get().run(f"git checkout {currentBranch}", True)

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

if __name__ == '__main__':
    result = main(parser.getArgs())
    if result is not None:
        print(result)
