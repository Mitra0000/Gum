class Node:
    def __init__(self, branch, commit, parent, children, is_owned, commitPrefix, commitSuffix):
        # The branch name eg. "aaaaa".
        self.branch = branch
        # The full commit hash.
        self.commit = commit
        # The parent commit node.
        self.parent = parent
        # List of child commit nodes.
        self.children = children
        # Boolean denoting whether the change is owned.
        self.is_owned = is_owned
        # Shortest unique commit hash prefix.
        self.commitPrefix = commitPrefix
        # Remainder of the shortened commit hash.
        self.commitSuffix = commitSuffix

    def __str__(self):
        return f"{{branch: {self.branch}, commit: {self.commit}, parent: {self.parent.branch if self.parent else None}, children: {[c.commit for c in self.children]}, is_owned: {self.is_owned}, commitPrefix: {self.commitPrefix}, commitSuffix: {self.commitSuffix}}}"
