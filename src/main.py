import sys

from branches import *
from commits import CommitManager
from traverser import Traverser
from util import *

class CommandParser:
    def __init__(self, commandRunner: CommandRunner):
        self.runner = commandRunner
        self.branchManager = BranchManager(self.runner)
        self.commitManager = CommitManager(self.runner, self.branchManager)

    def parse(self, args):
        command = args[0]
        if command == "add":
            if len(args) == 1:
                self.runner.runInProcess("git add -A")
            else:
                self.runner.runInProcess(f"git add {args[1]}")
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
            self.runner.runInProcess(f"git commit -m '{commitMessage}'")
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
            self.runner.runInProcess("git push")
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
            tree = self.setupXl()
            print(self.xl(tree, self.branchManager.getCommitForBranch(self.branchManager.getCurrentBranch())))
        else:
            print("Unknown gum command")
        
    def setupXl(self):
        branches = self.branchManager.getAllBranches()
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
        return self.commitManager.buildTreeFromCommits(parentsToCommits, commits)


    def xl(self, root: Node, currentHash: str):
        root.level = 0
        Node.getTrunk(root)
        root.markNodes()
        traverser = Traverser()
        traverser.preOrderTraversal(root)
        nodes = traverser.order[::-1]
        uniqueHashes = getUniqueCommitPrefixes([n.commitHash for n in nodes])
        clNumbers = self.branchManager.getUrlsForBranches()
        output = ""

        for i, x in enumerate(nodes):
            message = formatText(uniqueHashes[x.commitHash][0], underline=True, color=Color.Yellow)
            message += formatText(uniqueHashes[x.commitHash][1], color=Color.Yellow) + " " 
            message += self.runner.run(f"git log {x.commitHash} -1 --pretty=format:%s")
            # Print the commit message.
            if x.commitHash == currentHash:
                output += "| " * x.level + f"@ {message}\n"
            else:
                output += "| " * x.level + f"o {message}\n"
            
            if x.commitHash in clNumbers and clNumbers[x.commitHash] != "None":
                output += "| " * (x.level + 1) + clNumbers[x.commitHash] + "\n"

            # Print the author of the change.
            if x.isOwned:
                output += "| " * (x.level + 1) + formatText("Author: You", color=Color.Blue) + "\n"
            else:
                output += "| " * (x.level + 1) + formatText("Author: ", color=Color.Blue) + self.commitManager.getEmailForCommit(x.commitHash) + "\n"

            if i + 1 < len(nodes) and nodes[i+1].level < x.level:
                output += "| " * nodes[i+1].level + "|/\n"
            elif i + 1 < len(nodes) and nodes[i+1].level == x.level:
                output += "| " * x.level + "|\n"
            elif i + 1 < len(nodes) and nodes[i+1].level > x.level:
                output += "| " * (x.level + 1) + "\n"
        output += "~"
        return output
    

if __name__ == '__main__':
    parser = CommandParser(CommandRunner())
    parser.parse(sys.argv[1:])
