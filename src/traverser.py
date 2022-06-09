# Pre order traversal of nodes choosing the largest level first
class Traverser:
    def __init__(self):
        self.order = []

    def preOrderTraversal(self, node):
        if node.commitHash != "":
            self.order.append(node)
        children = sorted(node.children, key=lambda node:node.level, reverse=True)

        for i in children:
            self.preOrderTraversal(i)