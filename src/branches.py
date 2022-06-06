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
        return runCommand("git rev-parse --short " + reference)[:-1]