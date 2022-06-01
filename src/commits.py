import os

from branches import BranchManager
from xl import *

class CommitManager:
    @classmethod
    def buildTreeFromCommits(cls, parentsToCommits, commits):
        commitList = list(commits)
        nodes = [Node(i) for i in commitList]
        for i in parentsToCommits.values():
            for j in i:
                commits.remove(j)
        # Commits now contains the root(s)
        for i in parentsToCommits:
            nodes[commitList.index(i)].children.extend([nodes[commitList.index(j)] for j in parentsToCommits[i]])
        return nodes[commitList.index(commits.pop())]
    
    @classmethod
    def createCommitMessage(cls):
        output = "\n\n\n\nGUM: Enter a commit message. Lines beginning with 'GUM:' are removed.\nGUM: Leave commit message empty to cancel.\nGUM: --\nGUM: user: "
        output += runCommand("git config user.email") + "\n"
        files = runCommand("git status -s").split("\n")
        for line in files:
            if line == "" or line.startswith("?"):
                continue
            if line.startswith("A"):
                output += "GUM: Added " + line[2:]
            elif line.startswith("M"):
                output += "GUM: Modified " + line[2:]
            elif line.startswith("D"):
                output += "GUM: Deleted " + line[2:]

        filePath = "/tmp/gum_commit_message.txt"

        with open(filePath, "w") as f:
            f.write(output)

        os.system("nano " + filePath)
        commitMessage = []
        with open(filePath, "r") as f:
            content = f.read()
        if content == output:
            return None

        lines = content.split("\n")
        for line in lines:
            if line.startswith("GUM:") or line == ""  or line == "\n":
                continue
            commitMessage.append(line)
        
        if os.path.exists(filePath):
            os.remove(filePath)
        return "\n".join(commitMessage)
    
    @classmethod
    def getBranchForCommit(cls, commitHash: str) -> str:
        for branch in BranchManager.getAllBranches():
            if BranchManager.getCommitForBranch(branch) == commitHash:
                return branch
        return None