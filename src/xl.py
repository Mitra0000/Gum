from util import *

class Node:
    trunk = set()

    def __init__(self, commitHash=""):
        self.commitHash = commitHash
        self.children = []
        self.level = -1

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

def xl(root, currentHash):
    root.level = 0
    Node.getTrunk(root)
    root.markNodes()
    traverser = Traverser()
    traverser.preOrderTraversal(root)
    nodes = traverser.order[::-1]
    uniqueHashes = getUniqueCommitPrefixes([n.commitHash for n in nodes])
    for i, x in enumerate(nodes):
        message = formatText(uniqueHashes[x.commitHash][0], underline=True, color=Color.Yellow)
        message += formatText(uniqueHashes[x.commitHash][1], color=Color.Yellow) + " " 
        message += runCommand("git log " + x.commitHash + " -1 --pretty=format:%s")
        if x.commitHash == currentHash:
            print("| " * x.level + "@ " + message)
        else:
            print("| " * x.level + "o " + message)
        print("| " * (x.level + 1) + formatText(runCommand("git show --no-patch --no-notes " + x.commitHash + " --format=Author:%x20%ce")[:-1], color=Color.Blue))
        if i + 1 < len(nodes) and nodes[i+1].level < x.level:
            print("| " * nodes[i+1].level + "|/")
        elif i + 1 < len(nodes) and nodes[i+1].level == x.level:
            print("| " * x.level + "|")
        elif i + 1 < len(nodes) and nodes[i+1].level > x.level:
            print("| " * (x.level + 1))
    print("~")
    