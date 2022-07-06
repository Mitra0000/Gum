import bisect
from collections import defaultdict, deque
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
    branchesToParents, parentsToBranches = generateParentsAndCommits(branches)
    for branch in branches:
        commit = getCommitForBranch(branch)
        parent = branchesToParents[branch]
        children = parentsToBranches[branch]
        is_owned = isBranchOwned(branch)
        tree[branch] = Node(branch, commit, parent, children, is_owned)
    for branch in tree:
        tree[branch].parent = tree[tree[branch].parent] if tree[branch].parent else None
        tree[branch].children = [tree[i] for i in tree[branch].children]
    return tree

def getCommitForBranch(branch):
    return run(f"git rev-parse {branch}")[:-1]

def generateParentsAndCommits(branches):
    commits = set()
    unownedCommits = []
    parentsToCommits = defaultdict(set)
    commitsToParents = {}
    commitsToBranches = {}
    for branch in branches:
        commit = getCommitForBranch(branch)
        commits.add(commit)
        commitsToBranches[commit] = branch
        if not isBranchOwned(commit):
            bisect.insort(unownedCommits, (getDateForCommit(commit), commit))

    for branch in branches:
        if branch == "head":
            commitsToParents["head"] = None
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
        parentsToCommits[commitsToBranches[parent]].add(branch)
        commitsToParents[branch] = commitsToBranches[parent]
    return commitsToParents, parentsToCommits

def getDateForCommit(commitHash: str) -> str:
    return "".join(run(f"git show --no-patch --no-notes {commitHash} --pretty=format:%ci").split()[:-1])

def isBranchOwned(reference: str) -> str:
        return run(f"git show --no-patch --no-notes {reference} --format=%ce")[:-1] == run("git config user.email")[:-1]

class TreePrinter:
    output = []

    @classmethod
    def print(cls, tree):
        cls.output = []
        cls.output.append("~")
        cls.F(tree["head"], "| ", "")
    
    @classmethod
    def F(cls, node, bP, tP):
        cls.output.append(bP)
        cls.output.append(tP + "o " + node.branch)
        if len(node.children) == 1:
            cls.F(node.children[0], bP, tP)
        elif len(node.children) == 2:
            cls.F(node.children[0], bP[:-2] + "|/", tP + "| ")
            cls.F(node.children[1], bP, tP)
        elif len(node.children) > 2:
            cls.output.append(bP[:-2] + "|/")
            for child in node.children[:-2]:
                cls.F(child, bP + "|/", tP + "| | ")
            cls.F(node.children[-2], bP + " /", tP + "|   ")
            cls.F(node.children[-1], bP, tP)


def printTree(tree):
    TreePrinter.print(tree)
    return "\n".join(TreePrinter.output[::-1])
    LumberJack.getTrunk(tree["head"])
    lines = []
    lines.append("~")
    queue = deque()
    queue.append("head")
    interPrefix = ["| "]
    textPrefix = []
    while queue:
        current = tree[queue.popleft()]
        lines.append("".join(textPrefix) + "o " + current.branch)
        if len(current.children) == 0:
            continue
        elif len(current.children) == 1:
            lines.append("".join(interPrefix))
            queue.append(current.children[0].branch)
        elif len(current.children) == 2:
            continue
        elif len(current.children) > 2:
            continue

    return "\n".join(lines[::-1])


class LumberJack:
    trunk = set()

    @classmethod
    def getTrunk(cls, node: Node):
        best = None
        maxChildren = -1
        for child in node.children:
            if len(child.children) > maxChildren:
                maxChildren = len(child.children)
                best = child
        if best is not None:
            cls.trunk.add(best.branch)
            best.level = 0
            cls.getTrunk(best)

if __name__ == "__main__":
    tree = generateTree()
    # print({k: str(tree[k]) for k in tree})
    print(printTree(tree))