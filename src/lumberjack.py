from node import Node

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
            cls.trunk.add(best)
            best.level = 0
            cls.getTrunk(best)

    @classmethod
    def markNodes(cls, node: Node):
        if len(node.children) > 0:
            startingLevel = max(node.level, 1)
            addition = 0
            for child in node.children:
                if child not in cls.trunk:
                    child.level = startingLevel + addition
                    addition += 1
                cls.markNodes(child)