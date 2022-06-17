import os

from branches import *
from util import *

class CommitManager:
    def __init__(self, commandRunner: CommandRunner, branchManager: BranchManager):
        self.runner = commandRunner
        self.branchManager = branchManager
    
    def buildTreeFromCommits(self, parentsToCommits, commits):
        commitsToNodes = {i: Node(i, self.branchManager.isBranchOwned(i)) for i in commits}
        for i in parentsToCommits.values():
            for j in i:
                commits.remove(j)
        # Commits now contains the root(s)
        for i in parentsToCommits:
            if i in commitsToNodes:
                commitsToNodes[i].children.extend([commitsToNodes[j] for j in parentsToCommits[i]])
        if len(commits) > 1:
            heads = sorted(list(commits), key=self.getDateForCommit)
            for parent, child in zip(heads, heads[1:]):
                commitsToNodes[parent].children.append(commitsToNodes[child])
            return commitsToNodes[heads[0]]
        return commitsToNodes[commits.pop()]
    
    
    def createCommitMessage(self):
        output = "\n\n\n\nGUM: Enter a commit message. Lines beginning with 'GUM:' are removed.\nGUM: Leave commit message empty to cancel.\nGUM: --\nGUM: user: "
        output += self.runner.run("git config user.email") + "\n"
        files = self.runner.run("git status -s").split("\n")
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

        os.system(f"nano {filePath}")
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
    
    
    def getCommitForPrefix(self, prefix: str) -> str:
        results = getPrefixesForCommits([self.branchManager.getCommitForBranch(b) for b in self.branchManager.getAllBranches()])
        if prefix not in results:
            return prefix
        return prefix + results[prefix]
    
    def getParentOfCommit(self, commitHash: str) -> str:
        return self.branchManager.getCommitForBranch(commitHash + "^")

    
    def getBranchForCommit(self, commitHash: str) -> str:
        for branch in self.branchManager.getAllBranches():
            if self.branchManager.getCommitForBranch(branch) == commitHash:
                return branch
        return None
    
    
    def getDateForCommit(self, commitHash: str) -> str:
        return "".join(self.runner.run(f"git show --no-patch --no-notes {commitHash} --pretty=format:%ci").split()[:-1])
    
    
    def getEmailForCommit(self, commitHash: str) -> str:
        return self.runner.run(f"git show --no-patch --no-notes {commitHash} --format=%ce")[:-1]