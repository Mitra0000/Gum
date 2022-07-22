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

USER_EMAIL = "user@example.com"
ANOTHER_EMAIL = "someone.else@example.com"

class CommitNode:
    def __init__(self, commitHash, isOwned = False, children = None, parent = None, diff = None):
        self.commitHash = commitHash
        self.commitMessage = ""
        self.isOwned = isOwned
        self.children = children if children is not None else set()
        self.parent = parent
        self.diff = diff if diff is not None else dict()

class CommitTree:
    def __init__(self):
        self.nextHash = "aaaaa"
        root = CommitNode(self.nextHash)
        self.branchesToCommits = {"head": root}
        self.branches = set()
        self.branches.add("head")
        self.currentBranch = "head"
        self.workingChanges = {} # Format of { (filename, change_type) : "Contents" }
        self.createCommit("head", "This is the head of the repository.", False)
    
    def createBranch(self, branchName, parent):
        if branchName in self.branches:
            return "Could not create branch. Name already exists."
        if parent == None or parent not in self.branches:
            parent = self.currentBranch
        newBranch = CommitNode(self.getNode(parent).commitHash, parent = self.getNode(parent))
        self.getNode(parent).children.add(newBranch)
        self.branches.add(branchName)
        self.branchesToCommits[branchName] = newBranch
        self.updateCurrentBranchTo(branchName)
        return f"Created new branch '{branchName}'. Set to track {parent}."

    def createDetachedBranch(self, branchName):
        if branchName in self.branches:
            return "Could not create branch. Name already exists."
        newBranch = CommitNode(self.nextHash)
        self._incrementHash()
        self.branches.add(branchName)
        self.branchesToCommits[branchName] = newBranch
        return f"Created new branch '{branchName}'."


    def createCommit(self, branchName, commitMessage, isOwned = True):
        if branchName not in self.branches:
            return "Branch not found."
        node = self.branchesToCommits[branchName]
        node.commitHash = self.nextHash
        self._incrementHash()
        node.isOwned = isOwned
        node.commitMessage = commitMessage
        for change in self.workingChanges:
            if change[1] != "?":
                node.diff[change] = self.workingChanges[change]
    
    def updateCurrentBranchTo(self, branchName):
        if branchName not in self.branches:
            return None
        self.currentBranch = branchName
    
    def setParent(self, branchName, parent):
        oldParent = self.branchesToCommits[branchName].parent
        self.branchesToCommits[branchName].parent = parent
        if oldParent is not None:
            oldParent.children.remove(self.branchesToCommits[branchName])
        
    def getBranches(self):
        outputString = ""
        for branch in self.branches:
            if branch == self.currentBranch:
                outputString += f"* {branch}\n"
            else:
                outputString += f"  {branch}\n"
        return outputString
    
    def getNode(self, branchName):
        if branchName not in self.branchesToCommits:
            for branch in self.branchesToCommits:
                if str(self.branchesToCommits[branch].commitHash) == branchName:
                    return self.branchesToCommits[branch]
            return None
        return self.branchesToCommits[branchName]
    
    def findHash(self, branchName):
        node = self.getNode(branchName)
        return f"{node.commitHash}\n" if node is not None else None
    
    def removeBranch(self, branchName):
        if branchName not in self.branches:
            return f"error: branch '{branchName}' not found."
        self.branches.remove(branchName)
        node = self.branchesToCommits[branchName]
        for child in node.children:
            child.parent = None
        parent = node.parent
        if parent is not None:
            parent.children.remove(node)
    
    def _incrementHash(self):
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        commit = list(self.nextHash)
        for i in range(len(commit) - 1, -1, -1):
            if commit[i] != "z":
                commit[i] = alphabet[alphabet.find(commit[i]) + 1]
                break
            commit[i] = "a"
        self.nextHash = "".join(commit)

""" 
    A class representing a git repository for testing.
    Commands can be run on the repository and the commit 
    tree will be modified accordingly.
"""
class MockRepository:
    def __init__(self):
        self.commitTree = CommitTree()
    
    def addChanges(self, changes):
        self.commitTree.workingChanges.update(changes)

    def processCommand(self, args):
        args = args.split()
        assert args[0] == "git"
        command = args[1]
        if command == "add":
            if args[2] == "-A":
                # git add -A
                for change in self.commitTree.workingChanges:
                    if change[1] == "?":
                        newItem = {(change[0], "A"): self.commitTree.workingChanges[change]}
                        del self.commitTree.workingChanges[change]
                        self.commitTree.workingChanges.update(newItem)
            if args[2] == "-u":
                # git add -u
                return
        elif command == "branch":
            if len(args) == 2:
                # git branch
                return self.commitTree.getBranches()
            if len(args) == 4 and args[2] == "-D":
                # git branch -D {branch}
                branchName = args[3]
                return self.commitTree.removeBranch(branchName)
            elif args[2].startswith("--set-upstream-to="):
                if len(args) == 3:
                    if args[2].endswith("origin/main"):
                        # git branch --set-upstream-to=origin/main
                        self.commitTree.setParent(self.commitTree.currentBranch, None)
                        return f"{self.commitTree.currentBranch} now set to track 'origin/main'."
                    else:
                        # git branch --set-upstream-to={branch}
                        newParent = args[2].split("=")[1]
                        self.commitTree.setParent(self.commitTree.currentBranch, newParent)
                        return f"{self.commitTree.currentBranch} now set to track '{newParent}'."
                elif len(args) == 4:
                    if args[2] == "--set-upstream-to=origin/main" and args[3] == "head":
                        # git branch --set-upstream-to=origin/main head
                        self.commitTree.setParent("head", None)
                        return "head now set to track 'origin/main'."
        elif command == "checkout":
            if args[2] == "-b":
                if len(args) == 4:
                    # git checkout -b {new_branch}
                    return self.commitTree.createBranch(args[3], None)
                elif len(args) == 5:
                    # git checkout -b {new_branch} {parent}
                    return self.commitTree.createBranch(args[3], args[4])
            elif len(args) == 3:
                # git checkout {branch}
                self.commitTree.updateCurrentBranchTo(args[2])
                return
        elif command == "cl":
            if args[2] == "status":
                "git cl status -f --no-branch-color"
                return ""
        elif command == "commit":
            if args[2] == "-m":
                # git commit -m '{commit_message}'
                if len(self.commitTree.workingChanges) == 0:
                    return
                args = args[3:]
                commitMessage = " ".join(args)
                self.commitTree.createCommit(self.commitTree.currentBranch, commitMessage)
        elif command == "config":
            if args[2] == "user.email":
                # git config user.email
                return f"{USER_EMAIL}\n"
        elif command == "log":
            # git log {reference} -1 --pretty=format:%s
            return self.commitTree.getNode(args[2]).commitMessage.split("\n")[0]
        elif command == "pull":
            "git pull --rebase"
        elif command == "push":
            "git push"
        elif command == "rev-parse":
            if args[2] == "--abbrev-ref" and args[3] == "HEAD":
                # git rev-parse --abbrev-ref HEAD
                return f"{self.commitTree.currentBranch}\n"
            elif len(args) == 4 and args[2] == "--short":
                # git rev-parse --short {branch}
                return self.commitTree.findHash(args[3])
        elif command == "show":
            dataFormat = args[-1].split("%")[-1]
            if dataFormat == "ci":
                # git show --no-patch --no-notes {commit} --pretty=format:%ci
                return args[4] + " +1:00"
            elif dataFormat == "ce":
                # git show --no-patch --no-notes {commit} --format=%ce
                node = self.commitTree.getNode(args[4])
                if node is None:
                    return "unknown"
                return f"{USER_EMAIL}\n" if node.isOwned else f"{ANOTHER_EMAIL}\n"
        elif command == "status":
            "git status -s"
            "git status -s"
