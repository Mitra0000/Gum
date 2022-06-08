import os

from util import *

class BranchManager:
    @classmethod
    def getAllBranches(cls):
        """ Gets a list of all branches with the current branch at the end. """
        data = runCommand("git branch")
        data = data.split("\n")
        output = []
        current = ""
        for branch in data:
            if branch.startswith("*"):
                current = branch[2:]
                continue
            if branch == "":
                continue
            output.append(branch[2:])
        output.append(current)
        return output
    
    @classmethod
    def getCurrentBranch(cls):
        return runCommand("git rev-parse --abbrev-ref HEAD")[:-1]

    @classmethod
    def getNextBranch(cls):
        filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nextBranch.txt")
        with open(filename, "r") as f:
            branch = f.read()
        nextBranch = cls._getNextBranchNameFrom(branch)
        with open(filename, "w") as f:
            f.write(nextBranch)
        return branch
    
    @classmethod
    def _getNextBranchNameFrom(cls, branchName):
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        branchName = list(branchName)
        for i in range(len(branchName) - 1, -1, -1):
            if branchName[i] != "z":
                branchName[i] = alphabet[alphabet.find(branchName[i]) + 1]
                break
            branchName[i] = "a"
        return "".join(branchName)
    
    @classmethod
    def getCommitForBranch(cls, reference: str) -> str:
        return runCommand(f"git rev-parse --short {reference}")[:-1]

    @classmethod
    def isBranchOwned(cls, reference: str) -> str:
        return runCommand(f"git show --no-patch --no-notes {reference} --format=%ce")[:-1] == runCommand("git config user.email")[:-1]

class Node:
    trunk = set()

    def __init__(self, commitHash=""):
        self.commitHash = commitHash
        self.children = []
        self.level = -1
        self.isOwned = BranchManager.isBranchOwned(commitHash) if commitHash != "" else False

    def __str__(self):
        return str(self.commitHash)

    def __hash__(self):
        return hash(self.commitHash)

    @classmethod
    def getTrunk(cls, node):
        best = None
        maxChildren = -1
        for child in node.children:
            if len(child.children) > maxChildren:
                maxChildren = len(child.children)
                best = child
        if best is not None:
            Node.trunk.add(best)
            best.level = 0
            Node.getTrunk(best)

    def markNodes(self):
        if len(self.children) > 0:
            startingLevel = max(self.level, 1)
            addition = 0
            for child in self.children:
                if child not in Node.trunk:
                    child.level = startingLevel + addition
                    addition += 1
                child.markNodes()