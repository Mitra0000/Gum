class Node:
    def __init__(self, branch, commit, parent, children, is_owned, commitPrefix, commitSuffix):
        self.branch = branch
        self.commit = commit
        self.parent = parent
        self.children = children
        self.is_owned = is_owned
        self.commitPrefix = commitPrefix
        self.commitSuffix = commitSuffix

    def __str__(self):
        return f"{{branch: {self.branch}, commit: {self.commit}, parent: {self.parent.branch if self.parent else None}, children: {[c.commit for c in self.children]}, is_owned: {self.is_owned}, commitPrefix: {self.commitPrefix}, commitSuffix: {self.commitSuffix}}}"
