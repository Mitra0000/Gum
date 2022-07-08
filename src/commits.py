import os

import branches
from node import Node
from runner import CommandRunner as runner
from util import *

def buildTreeFromCommits(parentsToCommits, commits):
    commitsToNodes = {i: createNode(i) for i in commits}
    for i in parentsToCommits.values():
        for j in i:
            commits.remove(j)
    # Commits now contains the root(s)
    for i in parentsToCommits:
        if i in commitsToNodes:
            commitsToNodes[i].children.extend([commitsToNodes[j] for j in parentsToCommits[i]])
    if len(commits) > 1:
        heads = sorted(list(commits), key=getDateForCommit)
        for parent, child in zip(heads, heads[1:]):
            commitsToNodes[parent].children.append(commitsToNodes[child])
        return commitsToNodes[heads[0]]
    return commitsToNodes[commits.pop()]

def createNode(commitHash: str) -> Node:
    owned = branches.isBranchOwned(commitHash)
    return Node(commitHash, owned)

def createCommitMessage():
    output = "\n\n\n\nGUM: Enter a commit message. Lines beginning with 'GUM:' are removed.\nGUM: Leave commit message empty to cancel.\nGUM: --\nGUM: user: "
    output += runner.get().run("git config user.email") + "\n"
    files = runner.get().run("git status -s").split("\n")
    if files == [""]:
        print("No files to commit.")
        return None
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


def getCommitForPrefix(prefix: str) -> str:
    results = getPrefixesForCommits([branches.getCommitForBranch(b) for b in branches.getAllBranches()])
    if prefix not in results:
        return prefix
    return prefix + results[prefix]

def getParentOfCommit(commitHash: str) -> str:
    return branches.getCommitForBranch(commitHash + "^")

def getTitleOfCommit(commitHash: str) -> str:
    return runner.get().run(f"git log {commitHash} -1 --pretty=format:%s")

def getBranchForCommit(commitHash: str) -> str:
    for branch in branches.getAllBranches():
        if branches.getCommitForBranch(branch) == commitHash:
            return branch
    return None


def getDateForCommit(commitHash: str) -> str:
    return "".join(runner.get().run(f"git show --no-patch --no-notes {commitHash} --pretty=format:%ci").split()[:-1])


def getEmailForCommit(commitHash: str) -> str:
    return runner.get().run(f"git show --no-patch --no-notes {commitHash} --format=%ae")[:-1]