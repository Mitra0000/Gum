USER_EMAIL = "user@example.com"
ANOTHER_EMAIL = "someone.else@example.com"

class CommitNode:
    def __init__(self, commitHash, isOwned = False, children = None, parent = None, diff = None):
        self.commitHash = commitHash
        self.isOwned = isOwned
        self.children = children if children is not None else set()
        self.parent = parent
        self.diff = diff if diff is not None else dict()

class CommitTree:
    def __init__(self):
        self.nextHash = 1
        root = CommitNode(self.nextHash)
        self.nextHash += 1
        self.branchesToCommits = {"head": root}
        self.branches = set("head")
        self.currentBranch = "head"
        self.workingChanges = {} # Format of { (filename, change_type) : "Contents" }
    
    def createBranch(self, branchName, parent):
        if branchName in self.branches:
            return "Could not create branch. Name already exists."
        if parent == None or parent not in self.branches:
            parent = self.currentBranch
        newBranch = CommitNode(self.nextHash, True, parent = self.getNode(parent))
        self.nextHash += 1
        self.getNode(parent).children.add(newBranch)
        self.branches.add(branchName)
        self.branchesToCommits[branchName] = newBranch
        return f"Created new branch '{branchName}'. Set to track {parent}."
    
    def updateCurrentBranchTo(self, branchName):
        if branchName not in self.branches:
            return None
        self.currentBranch = branchName
    
    def setParent(self, branchName, parent):
        oldParent = self.branchesToCommits[branchName].parent
        self.branchesToCommits[branchName].parent = parent
        if oldParent is not None:
            oldParent.children.remove(self.branchesToCommits[branchName])
        
    def getBranches(self):
        outputString = ""
        for branch in self.branches:
            if branch == self.currentBranch:
                outputString += f"* {branch}\n"
            else:
                outputString += f"  {branch}\n"
        return outputString
    
    def getNode(self, branchName):
        if branchName not in self.branchesToCommits:
            return None
        return self.branchesToCommits[branchName]
    
    def findHash(self, branchName):
        node = self.getNode(branchName)
        return node if node is not None else None
    
    def removeBranch(self, branchName):
        if branchName not in self.branches:
            return f"error: branch '{branchName}' not found."
        self.branches.remove(branchName)
        node = self.branchesToCommits[branchName]
        for child in node.children:
            child.parent = None
        parent = node.parent
        if parent is not None:
            parent.children.remove(node)

""" 
    A class representing a git repository for testing.
    Commands can be run on the repository and the commit 
    tree will be modified accordingly.
"""
class MockRepository:
    def __init__(self):
        self.commitTree = CommitTree()

    def processCommand(self, args):
        args = args.split()
        assert args[0] == "git"
        command = args[1]
        if command == "add":
            "git add -A",
            "git add -u",
        elif command == "branch":
            if len(args) == 2:
                # git branch
                return self.commitTree.getBranches()
            if len(args) == 4 and args[2] == "-D":
                # git branch -D {branch}
                branchName = args[3]
                return self.commitTree.removeBranch(branchName)
            elif args[2].startswith("--set-upstream-to="):
                if len(args) == 3:
                    if args[2].endswith("origin/main"):
                        # git branch --set-upstream-to=origin/main
                        self.commitTree.setParent(self.commitTree.currentBranch, None)
                        return f"{self.commitTree.currentBranch} now set to track 'origin/main'."
                    else:
                        # git branch --set-upstream-to={branch}
                        newParent = args[2].split("=")[1]
                        self.commitTree.setParent(self.commitTree.currentBranch, newParent)
                        return f"{self.commitTree.currentBranch} now set to track '{newParent}'."
                elif len(args) == 4:
                    if args[2] == "--set-upstream-to=origin/main" and args[3] == "head":
                        # git branch --set-upstream-to=origin/main head
                        self.commitTree.setParent("head", None)
                        return "head now set to track 'origin/main'."
        elif command == "checkout":
            if args[2] == "-b":
                if len(args) == 4:
                    # git checkout -b {new_branch}
                    return self.commitTree.createBranch(args[3], None)
                elif len(args) == 5:
                    # git checkout -b {new_branch} {parent}
                    return self.commitTree.createBranch(args[3], args[4])
            elif len(args) == 3:
                # git checkout {branch}
                self.commitTree.updateCurrentBranchTo(args[2])
                return
        elif command == "cl":
            if args[2] == "status":
                "git cl status -f --no-branch-color",
        elif command == "commit":
            if args[2] == "-m":
                "git commit -m '{commitMessage}'",
        elif command == "config":
            if args[2] == "user.email":
                "git config user.email",
        elif command == "log":
            "git log {x.commitHash} -1 --pretty=format:%s",
        elif command == "pull":
            "git pull --rebase",
        elif command == "push":
            "git push",
        elif command == "rev-parse":
            if args[2] == "--abbrev-ref" and args[3] == "HEAD":
                # git rev-parse --abbrev-ref HEAD
                return self.commitTree.currentBranch
            elif len(args) == 4 and args[2] == "--short":
                # git rev-parse --short {branch}
                return self.commitTree.findHash(args[3])
        elif command == "show":
            dataFormat = args[-1].split("%")[-1]
            if dataFormat == "ci":
                "git show --no-patch --no-notes {commitHash} --pretty=format:%ci",
            elif dataFormat == "ce":
                # git show --no-patch --no-notes {commit} --format=%ce
                if self.commitTree.getNode(args[4]).isOwned:
                    return USER_EMAIL
                else:
                    return ANOTHER_EMAIL
        elif command == "status":
            "git status -s",
            "git status -s",
