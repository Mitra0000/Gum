import os
import subprocess
import sys

from branches import BranchManager
from commits import CommitManager
from util import *
from xl import *

def main():
    command = sys.argv[1]
    if command == "add":
        if len(sys.argv) == 2:
            os.system("git add -A")
        else:
            os.system("git add " + sys.argv[2])
    elif command == "init":
        runCommand("git branch -D head")
        runCommand("git checkout -b head")
        for branch in BranchManager.getAllBranches():
            if branch != "head":
                runCommand("git branch -D " + branch)
        runCommand("git pull --rebase")
    elif command == "test":
        print(CommitManager.getUniqueCommitNames([BranchManager.getCommitForBranch(b) for b in BranchManager.getAllBranches()]))
    elif command == "commit":
        commitMessage = CommitManager.createCommitMessage()
        if commitMessage is None:
            return
        currentBranch = BranchManager.getCurrentBranch()
        newBranch = BranchManager.getNextBranch()
        # runCommand("git new-branch --upstream_current " + newBranch) # Only works on Chromium.
        runCommand("git checkout -b " + newBranch)
        runCommand("git branch --set-upstream-to=" + currentBranch)
        runCommand("git add -u")
        os.system("git commit -m '" + commitMessage + "'")
        # Store the current branch name as x
        # Create a new branch called y
        # Set upstream of y to x
        # Add known changes to y
        # Commit with commitMessage to y
    elif command == "amend":
        # Need to look at rebasing dependent branches after amending.
        # Use git rebase-update to rebase a dependent branch.
        # runCommand("git add -A")
        # runCommand("git commit --amend --no-edit")
        print("Amend not implemented.")
    elif command == "prune":
        if len(sys.argv) <= 2:
            print("Please specify a hash to prune.")
        commitHash = sys.argv[2]
        branchName = CommitManager.getBranchForCommit(commitHash)
        if branchName is None:
            print("Could not find specified commit hash.")
            return
        runCommand("git branch -D " + branchName)
    elif command == "uc":
        os.system("git push")
    elif command == "status":
       out = runCommand("git status -s")
       print(formatText(out, bold=True))
    elif command == "update":
        if len(sys.argv) <= 2:
            print("Please specify a hash to update to.")
        commitHash = sys.argv[2]
        branchName = CommitManager.getBranchForCommit(commitHash)
        if branchName is None:
            print("Could not find specified commit hash.")
            return
        runCommand("git checkout " + branchName)
        print("Updated to " + commitHash)
    elif command == "xl":
        branches = BranchManager.getAllBranches()
        currentBranch = branches[-1]
        commits = set()
        parentsToCommits = {}
        for branch in branches:
            commit = BranchManager.getCommitForBranch(branch)
            commits.add(commit)
            if branch != "head":
                parent = BranchManager.getCommitForBranch(branch + "^")
                if parent not in parentsToCommits:
                    parentsToCommits[parent] = set()
                parentsToCommits[parent].add(commit)
        tree = CommitManager.buildTreeFromCommits(parentsToCommits, commits)
        xl(tree, BranchManager.getCommitForBranch(currentBranch))

    else:
        print("Unknown gum command")

if __name__ == '__main__':
    main()
