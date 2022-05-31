import os
import subprocess
import sys

from branches import BranchManager
from commits import CommitManager
from format import *
from xl import *

def main():
    command = sys.argv[1]
    if command == "commit":
        commitMessage = CommitManager.createCommitMessage()
        if commitMessage is None:
            return

        currentBranch = BranchManager.getCurrentBranch()
        newBranch = BranchManager.getNextBranch()
        runCommand("git checkout -b " + newBranch)
        runCommand("git branch --set-upstream-to=" + currentBranch)
        runCommand("git add -A")
        runCommand("git commit -m '" + commitMessage + "'")
        # Store the current branch name as x
        # Create a new branch called y
        # Set upstream of y to x
        # Add known changes to y
        # Commit with commitMessage to y
        # runCommand("git commit -m " + "\n".join(commitMessage))

    elif command == "uc":
        os.system("git push")
    elif command == "status":
       out = runCommand("git status -s")
       print(format(out, bold=True, color=Color.Green))
    elif command == "xl":
        branches = BranchManager.getAllBranches()
        currentBranch = branches[-1]
        commits = set()
        parentsToCommits = {}
        for branch in branches:
            commit = BranchManager.getCommitForBranch(branch)
            commits.add(commit)
            parent = BranchManager.getCommitForBranch(branch + "^")
            commits.add(parent)
            if parent not in parentsToCommits:
                parentsToCommits[parent] = set()
            parentsToCommits[parent].add(commit)
        tree = CommitManager.buildTreeFromCommits(parentsToCommits, commits)
        xl(tree, BranchManager.getCommitForBranch(currentBranch))

    else:
        print("Unknown gum command")

if __name__ == '__main__':
    main()
