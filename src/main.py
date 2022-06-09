import os
import subprocess
import sys

from branches import BranchManager
from commits import CommitManager
from util import *
from xl import *

class CommandParser:
    def __init__(self, commandRunner: CommandRunner):
        self.runner = commandRunner
        self.branchManager = BranchManager(self.runner)
        self.commitManager = CommitManager(self.runner, self.branchManager)

    def parse(self, args):
        command = args[0]
        if command == "add":
            if len(args) == 1:
                os.system("git add -A")
            else:
                os.system(f"git add {args[1]}")
        elif command == "init":
            self.runner.run("git branch -D head")
            self.runner.run("git checkout -b head")
            self.runner.run("git branch --set-upstream-to=origin/main head")
            for branch in self.branchManager.getAllBranches():
                if branch != "head":
                    self.runner.run(f"git branch -D {branch}")
            self.runner.run("git pull --rebase")
        elif command == "test":
            print(self.branchManager.getUrlsForBranches())
        elif command == "commit":
            commitMessage = self.commitManager.createCommitMessage()
            if commitMessage is None:
                return
            currentBranch = self.branchManager.getCurrentBranch()
            newBranch = self.branchManager.getNextBranch()
            if self.branchManager.isBranchOwned(currentBranch):
                # self.runner.run(f"git new-branch --upstream_current {newBranch}") # Only works on Chromium.
                self.runner.run(f"git checkout -b {newBranch}")
                self.runner.run(f"git branch --set-upstream-to={currentBranch}")
            else:
                # If we're currently on an unowned node we don't want to set an upstream so that we can upload to Gerrit.
                self.runner.run(f"git checkout -b {newBranch} {self.branchManager.getCommitForBranch(currentBranch)}")
                self.runner.run("git branch --set-upstream-to=origin/main")
            self.runner.run("git add -u")
            os.system(f"git commit -m '{commitMessage}'")
            # Store the current branch name as x
            # Create a new branch called y
            # Set upstream of y to x
            # Add known changes to y
            # Commit with commitMessage to y
        elif command == "amend":
            # Need to look at rebasing dependent branches after amending.
            # Use git rebase-update to rebase a dependent branch.
            # self.runner.run("git add -A")
            # self.runner.run("git commit --amend --no-edit")
            print("Amend not implemented.")
        elif command == "prune":
            if len(args) == 1:
                print("Please specify a hash to prune.")
            commitHash = args[1]
            commit = self.commitManager.getCommitForPrefix(commitHash)
            if commit != None:
                commitHash = commit
            branchName = self.commitManager.getBranchForCommit(commitHash)
            if branchName is None:
                print("Could not find specified commit hash.")
                return
            self.runner.run(f"git branch -D {branchName}")
        elif command == "uc":
            os.system("git push")
        elif command == "status":
            out = self.runner.run("git status -s")
            print(formatText(out, bold=True))
        elif command == "update":
            if len(args) == 1:
                print("Please specify a hash to update to.")
            commitHash = args[1]
            commit = self.commitManager.getCommitForPrefix(commitHash)
            if commit != None:
                commitHash = commit
            branchName = self.commitManager.getBranchForCommit(commitHash)
            if branchName is None:
                print("Could not find specified commit hash.")
                return
            self.runner.run(f"git checkout {branchName}")
            print(f"Updated to {commitHash}")
        elif command == "xl":
            branches = self.branchManager.getAllBranches()
            currentBranch = branches[-1]
            commits = set()
            parentsToCommits = {}
            for branch in branches:
                commit = self.branchManager.getCommitForBranch(branch)
                commits.add(commit)
                if branch != "head":
                    parent = self.branchManager.getCommitForBranch(f"{branch}^")
                    if parent not in parentsToCommits:
                        parentsToCommits[parent] = set()
                    parentsToCommits[parent].add(commit)
            tree = self.commitManager.buildTreeFromCommits(parentsToCommits, commits)
            xl(tree, self.branchManager.getCommitForBranch(currentBranch), self.runner, self.branchManager, self.commitManager)

        else:
            print("Unknown gum command")

if __name__ == '__main__':
    parser = CommandParser(CommandRunner())
    parser.parse(sys.argv[1:])
