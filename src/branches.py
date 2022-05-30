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
    def getCommitForBranch(cls, reference: str) -> str:
        return runCommand("git rev-parse --short " + reference)[:-1]