import os

from cacher import Cacher
from util import *

class BranchManager:
    def __init__(self, commandRunner: CommandRunner):
        self.runner = commandRunner

    
    def getAllBranches(self):
        """ Gets a list of all branches with the current branch at the end. """
        data = self.runner.run("git branch")
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
        if current != "":
            output.append(current)
        return output
    
    
    def getCurrentBranch(self):
        return self.runner.run("git rev-parse --abbrev-ref HEAD")[:-1]

    
    def getNextBranch(self):
        filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nextBranch.txt")
        with open(filename, "r") as f:
            branch = f.read()
        branches = self.getAllBranches()
        for b in branches:
            if b == "head":
                continue
            if b >= branch:
                branch = self._getNextBranchNameFrom(b)

        nextBranch = self.getNextBranchNameFrom(branch)
        with open(filename, "w") as f:
            f.write(nextBranch)
        return branch
    
    
    def getNextBranchNameFrom(self, branchName):
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        branchName = list(branchName)
        for i in range(len(branchName) - 1, -1, -1):
            if branchName[i] != "z":
                branchName[i] = alphabet[alphabet.find(branchName[i]) + 1]
                break
            branchName[i] = "a"
        return "".join(branchName)
    
    
    def getCommitForBranch(self, reference: str) -> str:
        return self.runner.run(f"git rev-parse --short {reference}")[:-1]
    
    
    def getUrlsForBranches(self):
        branchesToUrls = {}
        output = self.runner.run("git cl status -f --no-branch-color")
        output = output.split("\n")[1:]
        for i in range(len(output)):
            if output[i] == "":
                break

            data = output[i].strip()
            if data.startswith("*"):
                data = data[2:]
            data = data.split()
            branchesToUrls[self.getCommitForBranch(data[0])] = data[2]
        Cacher.cacheClNumbers(branchesToUrls)
        return branchesToUrls

    
    def isBranchOwned(self, reference: str) -> str:
        return self.runner.run(f"git show --no-patch --no-notes {reference} --format=%ce")[:-1] == self.runner.run("git config user.email")[:-1]