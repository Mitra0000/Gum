import bisect
from collections import defaultdict, deque
import sys

from branches import BranchManager
from cacher import Cacher
from commits import CommitManager
from lumberjack import LumberJack
from node import Node
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
            return self.updateHead()
        elif command == "commit":
            commitMessage = self.commitManager.createCommitMessage()
            if commitMessage is None:
                return ""
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
            print("Amending changes.")
            self.runner.run("git add -u")
            self.runner.run("git commit --amend --no-edit")
            print("Rebasing dependent branches.")
            self.runner.runInProcess("git rebase-update --no-fetch")
            return
        elif command == "diff":
            self.runner.runInProcess("git diff")
        elif command == "fix":
            self.runner.runInProcess("git cl format")
        elif command == "prune":
            if len(args) == 1:
                return "Please specify a hash to prune."
            commitHash = args[1]
            commit = self.commitManager.getCommitForPrefix(commitHash)
            if commit != None:
                commitHash = commit
            branchName = self.commitManager.getBranchForCommit(commitHash)
            if branchName is None:
                return "Could not find specified commit hash."
            self.runner.run(f"git branch -D {branchName}")
        elif command == "uc" or command == "uploadchain":
            Cacher.invalidateClNumbers()
            originalRef = self.branchManager.getCurrentBranch()
            currentRef = originalRef
            commitStack = []
            while self.branchManager.isBranchOwned(currentRef):
                commitStack.append(currentRef)
                currentRef += "^"
            urls = []
            while commitStack:
                commitRef = commitStack.pop()
                commit = self.branchManager.getCommitForBranch(commitRef)
                branch = self.commitManager.getBranchForCommit(commit)
                self.runner.run(f"git checkout {branch}")
                self.runner.runInProcess("git cl upload -f")
                urls.append(commit)
            commitsToUrls = self.branchManager.getUrlsForBranches()
            print(f"Uploaded {len(urls)} CLs.")
            for commit in urls:
                if commit in commitsToUrls:
                    print(commitsToUrls[commit], ":", self.runner.run(f"git log {commit} -1 --pretty=format:%s"))
        elif command == "ut" or command == "uploadtree":
            Cacher.invalidateClNumbers()
            self.runner.runInProcess("git cl upload -f --dependencies")
        elif command == "rebase":
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
            destinationCommit = self.commitManager.getCommitForPrefix(destinationCommit)
            sourceCommit = self.commitManager.getCommitForPrefix(sourceCommit)
            if sourceCommit == "" or destinationCommit == "":
                return
            sourceBranch = self.commitManager.getBranchForCommit(sourceCommit)
            destinationBranch = self.commitManager.getBranchForCommit(destinationCommit)
            self.runner.runInProcess(f"git rebase --onto {destinationCommit} {self.commitManager.getParentOfCommit(sourceCommit)} {sourceCommit}")
            self.runner.run(f"git checkout -B {sourceBranch} HEAD")
            if self.branchManager.isBranchOwned(destinationBranch):
                self.runner.run(f"git branch --set-upstream-to={destinationBranch} {sourceBranch}")
            else:
                self.runner.run(f"git branch --unset-upstream {sourceBranch}")
            return
        elif command == "status":
            out = self.runner.run("git status -s")
            if out.strip() == "":
                return None
            return formatText(out, bold=True)
        elif command == "sync":
            currentBranch = self.branchManager.getCurrentBranch()
            if not self.branchManager.isBranchOwned(currentBranch):
                return
            # Need to traverse and rebase all children.
            newBranch = self.branchManager.getNextBranch()
            self.runner.run("git checkout head")
            self.runner.run(f"git checkout -b {newBranch}")
            self.runner.run(f"git branch --set-upstream-to=origin/main {newBranch}")
            self.runner.run("git pull")
            self.updateHead()
            # Move commit and children onto new branch.
            self.runner.run(f"git checkout {currentBranch}")
            self.runner.run(f"git rebase {newBranch}")
        elif command == "update":
            if len(args) == 1:
                return "Please specify a hash to update to."
            commitHash = args[1]
            commit = self.commitManager.getCommitForPrefix(commitHash)
            if commit != None:
                commitHash = commit
            branchName = self.commitManager.getBranchForCommit(commitHash)
            if branchName is None:
                return "Could not find specified commit hash."
            self.runner.run(f"git checkout {branchName}")
            return f"Updated to {commitHash}"
        elif command == "xl":
            tree = self.generateTree()
            return self.xl(tree, self.branchManager.getCommitForBranch(self.branchManager.getCurrentBranch()))
        else:
            return "Unknown gum command"
        
    def generateTree(self):
        commits, parentsToCommits = self.generateParentsAndCommits()
        return self.commitManager.buildTreeFromCommits(parentsToCommits, commits)


    def xl(self, root: Node, currentHash: str):
        root.level = 0
        LumberJack.getTrunk(root)
        LumberJack.markNodes(root)
        traverser = Traverser()
        traverser.preOrderTraversal(root)
        nodes = traverser.order[::-1]
        uniqueHashes = getUniqueCommitPrefixes([n.commitHash for n in nodes])
        clNumbers = Cacher.getCachedClNumbers()
        if len(clNumbers) == 0:
            clNumbers = self.branchManager.getUrlsForBranches()
        output = ""

        for i, node in enumerate(nodes):
            line1 = formatText(uniqueHashes[node.commitHash][0], underline=True, color=Color.Yellow)
            line1 += formatText(uniqueHashes[node.commitHash][1], color=Color.Yellow) + " " 
            
            # Print the author of the change.
            line1 += formatText("Author: ", color = Color.Blue)
            line1 += "You " if node.isOwned else abbreviateText(self.commitManager.getEmailForCommit(node.commitHash), 30) + " "

            # Print CL number.
            if node.commitHash in clNumbers and clNumbers[node.commitHash] != "None":
                line1 += clNumbers[node.commitHash]

            output += "| " * node.level
            output += f"@ {line1}\n" if node.commitHash == currentHash else f"o {line1}\n"
            
            # Print the commit message.
            output += "| " * (node.level + 1) + self.commitManager.getTitleOfCommit(node.commitHash) + "\n"

            if i + 1 < len(nodes) and nodes[i+1].level < node.level:
                output += "| " * nodes[i+1].level + "|/\n"
            elif i + 1 < len(nodes) and nodes[i+1].level == node.level:
                output += "| " * node.level + "|\n"
            elif i + 1 < len(nodes) and nodes[i+1].level > node.level:
                output += "| " * (node.level + 1) + "\n"
        output += "~"
        return output
    
    def generateParentsAndCommits(self):
        branches = self.branchManager.getAllBranches()
        commits = set()
        unownedCommits = []
        parentsToCommits = defaultdict(set)
        for branch in branches:
            commit = self.branchManager.getCommitForBranch(branch)
            commits.add(commit)
            if not self.branchManager.isBranchOwned(commit):
                bisect.insort(unownedCommits, (self.commitManager.getDateForCommit(commit), commit))

        for branch in branches:
            commit = self.branchManager.getCommitForBranch(branch)
            if branch == "head":
                continue
            parent = self.branchManager.getCommitForBranch(f"{branch}^")
            if parent not in commits:
                parentDate = self.commitManager.getDateForCommit(parent)
                for i in range(len(unownedCommits)):
                    if unownedCommits[i][0] > parentDate:
                        parent = unownedCommits[i - 1][1]
                        break
                else:
                    parent = unownedCommits[-1][1]
            parentsToCommits[parent].add(commit)
        return commits, parentsToCommits

    def updateHead(self):
        unownedBranches = []
        headCommit = self.branchManager.getCommitForBranch("head")
        for branch in self.branchManager.getAllBranches():
            if self.commitManager.getParentOfCommit(branch) == headCommit:
                return
            if not self.branchManager.isBranchOwned(branch):
                unownedBranches.append(branch)
        
        unownedBranches = sorted(unownedBranches, key=self.commitManager.getDateForCommit)
        if len(unownedBranches) < 2:
            print("Not working")
            return
        assert unownedBranches[0] == "head"
        newHead = unownedBranches[1]
        currentBranch = self.branchManager.getCurrentBranch()
        self.runner.run("git checkout head")
        self.runner.run(f"git pull origin {self.branchManager.getCommitForBranch(newHead)}")
        self.runner.run(f"git branch -D {newHead}") 
        self.runner.run(f"git checkout {currentBranch}")       

if __name__ == '__main__':
    parser = CommandParser(CommandRunner())
    result = parser.parse(sys.argv[1:])
    if result is not None:
        print(result)
