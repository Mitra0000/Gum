class Node:
    def __init__(self, branch, commit, parent, children, is_owned):
        self.branch = branch
        self.commit = commit
        self.parent = parent
        self.children = children
        self.is_owned = is_owned

    def __str__(self):
        return f"{{branch: {self.branch}, commit: {self.commit}, parent: {self.parent.branch if self.parent else None}, children: {[c.commit for c in self.children]}, is_owned: {self.is_owned}}}"
