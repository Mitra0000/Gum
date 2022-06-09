from branches import *
from commits import CommitManager
from util import *

# Pre order traversal choosing the largest level first
class Traverser:
    def __init__(self):
        self.order = []

    def preOrderTraversal(self, node):
        if node.commitHash != "":
            self.order.append(node)
        children = sorted(node.children, key=lambda node:node.level, reverse=True)

        for i in children:
            self.preOrderTraversal(i)

def xl(root: Node, currentHash: str, runner: CommandRunner, branchManager: BranchManager, commitManager):
    root.level = 0
    Node.getTrunk(root)
    root.markNodes()
    traverser = Traverser()
    traverser.preOrderTraversal(root)
    nodes = traverser.order[::-1]
    uniqueHashes = getUniqueCommitPrefixes([n.commitHash for n in nodes])
    clNumbers = branchManager.getUrlsForBranches()
    for i, x in enumerate(nodes):
        message = formatText(uniqueHashes[x.commitHash][0], underline=True, color=Color.Yellow)
        message += formatText(uniqueHashes[x.commitHash][1], color=Color.Yellow) + " " 
        message += runner.run(f"git log {x.commitHash} -1 --pretty=format:%s")
        # Print the commit message.
        if x.commitHash == currentHash:
            print("| " * x.level + "@ " + message)
        else:
            print("| " * x.level + "o " + message)
        
        if x.commitHash in clNumbers and clNumbers[x.commitHash] != "None":
            print("| " * (x.level + 1) + clNumbers[x.commitHash])

        # Print the author of the change.
        if x.isOwned:
            print("| " * (x.level + 1) + formatText("Author: You", color=Color.Blue))
        else:
            print("| " * (x.level + 1) + formatText("Author: ", color=Color.Blue) + commitManager.getEmailForCommit(x.commitHash))

        if i + 1 < len(nodes) and nodes[i+1].level < x.level:
            print("| " * nodes[i+1].level + "|/")
        elif i + 1 < len(nodes) and nodes[i+1].level == x.level:
            print("| " * x.level + "|")
        elif i + 1 < len(nodes) and nodes[i+1].level > x.level:
            print("| " * (x.level + 1))
    print("~")
    