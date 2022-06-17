import bisect
from collections import defaultdict
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
            return self.commitManager.getParentOfCommit("0ee1ae45d99b9")
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
            # Need to look at rebasing dependent branches after amending.
            # Use git rebase-update to rebase a dependent branch.
            # self.runner.run("git add -A")
            # self.runner.run("git commit --amend --no-edit")
            return "Amend not implemented."
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
            if sourceCommit == "" or destinationCommit == "":
                return
            self.runner.runInProcess(f"git rebase --onto {self.commitManager.getCommitForPrefix(destinationCommit)} {self.commitManager.getParentOfCommit(self.commitManager.getCommitForPrefix(sourceCommit))}")
        elif command == "status":
            out = self.runner.run("git status -s")
            if out.strip() == "":
                return None
            return formatText(out, bold=True)
        elif command == "sync":
            # Need to traverse and rebase all children.
            newBranch = self.branchManager.getNextBranch()
            self.runner.run("git checkout head")
            self.runner.run(f"git checkout -b {newBranch}")
            self.runner.run(f"git branch --set-upstream-to=origin/main {newBranch}")
            self.runner.run("git pull")
            self.updateHead()
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
            tree = self.setupXl()
            return self.xl(tree, self.branchManager.getCommitForBranch(self.branchManager.getCurrentBranch()))
        else:
            return "Unknown gum command"
        
    def setupXl(self):
        commits, parentsToCommits = self.generateParentsAndCommits()
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
            line1 = formatText(uniqueHashes[x.commitHash][0], underline=True, color=Color.Yellow)
            line1 += formatText(uniqueHashes[x.commitHash][1], color=Color.Yellow) + " " 
            
            # Print the author of the change.
            if x.isOwned:
                line1 += formatText("Author: You ", color=Color.Blue)
            else:
                line1 += formatText("Author: ", color=Color.Blue) + self.commitManager.getEmailForCommit(x.commitHash) + " "

            # Print CL number.
            if x.commitHash in clNumbers and clNumbers[x.commitHash] != "None":
                line1 += clNumbers[x.commitHash]

            if x.commitHash == currentHash:
                output += "| " * x.level + f"@ {line1}\n"
            else:
                output += "| " * x.level + f"o {line1}\n"
            
            # Print the commit message.
            output += "| " * (x.level + 1) + self.runner.run(f"git log {x.commitHash} -1 --pretty=format:%s") + "\n"

            if i + 1 < len(nodes) and nodes[i+1].level < x.level:
                output += "| " * nodes[i+1].level + "|/\n"
            elif i + 1 < len(nodes) and nodes[i+1].level == x.level:
                output += "| " * x.level + "|\n"
            elif i + 1 < len(nodes) and nodes[i+1].level > x.level:
                output += "| " * (x.level + 1) + "\n"
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
        commits, parentsToCommits = self.generateParentsAndCommits()
        headCommit = self.branchManager.getCommitForBranch("head")
        commits.remove(headCommit)
        if headCommit in parentsToCommits:
            return
        for parent in parentsToCommits.keys():
            commits.add(parent)
        for children in parentsToCommits.values():
            for child in children:
                commits.remove(child)
        newHead = ""
        if len(commits) == 0:
            return
        elif len(commits) == 1:
            newHead = self.runner.run(f"git rev-parse {commits.pop()}")
        else:
            heads = sorted(list(commits), key=self.commitManager.getDateForCommit)
            newHead = self.runner.run(f"git rev-parse {heads[0]}")

        currentBranch = self.branchManager.getCurrentBranch()
        self.runner.runInProcess("git checkout head")
        self.runner.runInProcess(f"git pull origin {newHead}")
        self.runner.runInProcess(f"git checkout {currentBranch}")

if __name__ == '__main__':
    parser = CommandParser(CommandRunner())
    result = parser.parse(sys.argv[1:])
    if result is not None:
        print(result)
