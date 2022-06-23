import bisect
from collections import defaultdict
import subprocess

from node import Node

def run(command: str) -> str:
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    return out.decode("utf-8")

def getAllBranches():
    """ Gets a list of all branches with the current branch at the end. """
    data = run("git branch")
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

def generateTree():
    branches = getAllBranches()
    tree = {}
    commitsToParents, parentsToCommits = generateParentsAndCommits()
    for branch in branches:
        commit = getCommitForBranch(branch)
        parent = commitsToParents[branch]
        children = parentsToCommits[commit]
        is_owned = isBranchOwned(branch)
        tree[branch] = Node(branch, commit, parent, children, is_owned)
    for branch in tree:
        tree[branch].parent = tree[tree[branch].parent] if tree[branch].parent else None
    return tree

def getParentOfCommit(parentsToCommits, commit):
    for parent in parentsToCommits:
        if commit in parentsToCommits[parent]:
            return parent
    return None

def getCommitForBranch(branch):
    return run(f"git rev-parse {branch}")[:-1]

def toBranch(commit):
    return run(f"git name-rev --name-only {commit}")

def generateParentsAndCommits():
    branches = getAllBranches()
    commits = set()
    unownedCommits = []
    parentsToCommits = defaultdict(set)
    commitsToParents = {}
    for branch in branches:
        commit = getCommitForBranch(branch)
        commits.add(commit)
        if not isBranchOwned(commit):
            bisect.insort(unownedCommits, (getDateForCommit(commit), commit))

    for branch in branches:
        if branch == "head":
            continue
        parent = getCommitForBranch(f"{branch}^")
        if parent not in commits:
            parentDate = getDateForCommit(parent)
            for i in range(len(unownedCommits)):
                if unownedCommits[i][0] > parentDate:
                    parent = unownedCommits[i - 1][1]
                    break
            else:
                parent = unownedCommits[-1][1]
        parentsToCommits[toBranch(parent)].add(branch)
        commitsToParents[commit] = toBranch(parent)
    return commitsToParents, parentsToCommits

def getDateForCommit(commitHash: str) -> str:
    return "".join(run(f"git show --no-patch --no-notes {commitHash} --pretty=format:%ci").split()[:-1])

def isBranchOwned(reference: str) -> str:
        return run(f"git show --no-patch --no-notes {reference} --format=%ce")[:-1] == run("git config user.email")[:-1]

if __name__ == "__main__":
    tree = generateTree()
    print({k: str(tree[k]) for k in tree})