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
import status
from tree import Tree
from tree_printer import TreePrinter
from util import *


def main():
    argparser = parser.getParser()
    args = argparser.parse_known_args()
    args = argparser.parse_args(args[1], args[0])

    command = args.command

    if command != "continue" and (
            branches.isRebaseInProgress() or
            Cacher.getCachedKey("REBASE_QUEUE") is not None):
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
        originalBranch = branches.getCurrentBranch()
        if not branches.isBranchOwned(originalBranch):
            return "You cannot amend to an unowned branch."
        print("Amending changes.")
        allChildren = Tree.getRecursiveChildrenFrom(originalBranch)
        runner.get().run("git add -u", True)
        runner.get().run("git commit --amend --no-edit", True)
        if len(allChildren) == 0:
            return "No dependent branches to rebase."
        print("Rebasing dependent branches.")
        branches.rebaseBranches(allChildren, originalBranch)
        return

    elif command == "commit":
        commitMessage = args.message if args.message else commits.createCommitMessage(
        )
        if commitMessage is None or commitMessage == "":
            return "Commit cancelled due to empty commit message."
        currentBranch = branches.getCurrentBranch()
        newBranch = branches.getNextBranch()
        if branches.isBranchOwned(currentBranch):
            runner.get().run(f"git checkout -b {newBranch}", True)
            runner.get().run(f"git branch --set-upstream-to={currentBranch}",
                             True)
        else:
            # If we're currently on an unowned node we don't want to set an
            # upstream so that we can upload to Gerrit.
            runner.get().run(
                f"git checkout -b {newBranch} {branches.getCommitForBranch(currentBranch)}",
                True)
            runner.get().run("git branch --set-upstream-to=origin/main", True)
        runner.get().run("git add -u", True)
        runner.get().runInProcess(f"git commit -m '{commitMessage}'")

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

    elif command == "forget":
        # Flatten the parsed filenames.
        files = [item for inner in args.files for item in inner]
        runner.get().runInProcess(f"git rm --cached {' '.join(files)}")

    elif command == "init":
        if not args.force:
            userContinue = input(
                "This will delete all current changes in your repository. " +
                "Do you wish to continue (y/N)? ")
            if userContinue.lower() != "y":
                return
        runner.get().run("git branch -D head", True)
        runner.get().run("git checkout -b head", True)
        runner.get().run("git branch --set-upstream-to=origin/main head", True)
        for branch in branches.getAllBranches():
            if branch != "head":
                runner.get().run(f"git branch -D {branch}", True)
        runner.get().run("git pull --rebase", True)

    elif command == "patch":
        newbranch = branches.getNextBranch()
        runner.get().runInProcess(
            f"git cl patch -b {newbranch} {args.cl} {'--force' if not args.copy else ''}"
        )

    elif command == "prune":
        commit = commits.getSingleCommitForPrefix(args.commit)
        if commit != None:
            args.commit = commit
        branchName = commits.getBranchForCommit(args.commit)
        if branchName is None:
            return "Could not find specified commit hash."
        runner.get().run(f"git branch -D {branchName}", True)

    elif command == "rebase":
        destinationCommit = commits.getSingleCommitForPrefix(args.destination)
        sourceCommit = commits.getSingleCommitForPrefix(args.source)
        if sourceCommit is None or destinationCommit is None:
            return f"Could not find specified commit: {args.source if sourceCommit == '' else args.destination}"
        sourceBranch = commits.getBranchForCommit(sourceCommit)
        destinationBranch = commits.getBranchForCommit(destinationCommit)
        runner.get().runInProcess(
            f"git rebase --onto {destinationCommit} {commits.getParentOfCommit(sourceCommit)} {sourceCommit}"
        )
        runner.get().run(f"git checkout -B {sourceBranch} HEAD", True)
        if branches.isBranchOwned(destinationBranch):
            runner.get().run(
                f"git branch --set-upstream-to={destinationBranch} {sourceBranch}",
                True)
        else:
            runner.get().run(f"git branch --unset-upstream {sourceBranch}",
                             True)
        updateHead()
        return

    elif command == "revert":
        # Flatten the parsed filenames.
        files = [item for inner in args.files for item in inner]
        runner.get().runInProcess(
            f"git restore --staged --worktree -s HEAD {' '.join(files)}")

    elif command == "status":
        return status.getStatus()

    elif command == "sync":
        currentBranch = branches.getCurrentBranch()
        if not branches.isBranchOwned(currentBranch):
            return "Syncing unowned branches is not implemented yet"
        # Need to traverse and rebase all children.
        newBranch = branches.getNextBranch()
        runner.get().run("git checkout head", True)
        runner.get().run(f"git checkout -b {newBranch}", True)
        runner.get().run(
            f"git branch --set-upstream-to=origin/main {newBranch}", True)
        print("Fetching changes from remote.")
        runner.get().runInProcess("git pull")

        runner.get().run(f"git checkout {currentBranch}", True)

        if branches.getCommitForBranch(
                newBranch) == branches.getCommitForBranch("head"):
            # Repository was already up to date.
            runner.get().run(f"git branch -D {newBranch}", True)
            return
        # Move commit and children onto new branch.
        print("Rebasing changes onto new head.")
        runner.get().run(f"git rebase {newBranch}", True)

        originalBranch = branches.getCurrentBranch()
        allChildren = Tree.getRecursiveChildrenFrom(originalBranch)
        branches.rebaseBranches(allChildren, originalBranch)

        Tree.cleanup()
        updateHead()

    elif command == "test":
        return commits.getSingleCommitForPrefix(input())

    elif command == "unamend":
        runner.get().run("git reset --soft HEAD@{1}")

    elif command == "uncommit":
        tree = Tree.get()
        currentBranch = branches.getCurrentBranch()
        runner.get().run("git reset --soft HEAD^", True)
        runner.get().run(f"git checkout {tree[currentBranch].parent.branch}",
                         True)
        runner.get().run(f"git branch -D {currentBranch}", True)

    elif command == "update":
        if status.getStatus() is not None:
            return "Cannot update with uncommitted changes.\nPlease commit/restore the changes and try again."
        commit = commits.getSingleCommitForPrefix(args.commit)
        if commit != None:
            args.commit = commit
        branchName = commits.getBranchForCommit(args.commit)
        if branchName is None:
            return "Could not find specified commit hash."
        print("Processing file changes...")
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
            returnCode = runner.get().runInProcessWithReturnCode(
                "git cl upload -f")
            if returnCode == 0:
                urls.append(commit)
        if len(urls) == 0:
            return "Upload failed."
        commitsToUrls = branches.getUrlsForBranches()
        print(f"Uploaded {len(urls)} CLs.")
        for commit in urls:
            if commit in commitsToUrls:
                print(
                    commitsToUrls[commit], ":",
                    runner.get().run(f"git log {commit} -1 --pretty=format:%s"))

    elif command == "uploadtree" or command == "ut":
        Cacher.invalidateKey(Cacher.CL_NUMBERS)
        runner.get().runInProcess("git cl upload -f --dependencies")

    elif command == "xl":
        tree = Tree.get()
        TreePrinter.print(tree["head"])

    else:
        argparser.print_help()


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
    runner.get().run(f"git pull origin {commits.getFullCommitHash(newHead)}",
                     True)
    runner.get().run(f"git branch -D {newHead}", True)
    runner.get().run(f"git checkout {currentBranch}", True)


if __name__ == '__main__':
    result = main()
    if result is not None:
        print(result)
