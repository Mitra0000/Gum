class Node:
    def __init__(self, commitHash: str = "", isOwned: bool = False):
        self.commitHash = commitHash
        self.children = []
        self.level = -1
        self.isOwned = isOwned

    def __str__(self):
        return str(self.commitHash)

    def __hash__(self):
        return hash(self.commitHash)