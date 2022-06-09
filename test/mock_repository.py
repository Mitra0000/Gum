""" 
    A class representing a git repository for testing.
    Commands can be run on the repository and the commit 
    tree will be modified accordingly.
"""
class MockRepository:
    def processCommand(args):
        args = args.split()
        assert args[0] == "git"
        command = args[1]
        if command == "add":
            "git add -A",
            "git add -u",
        elif command == "branch":
            if len(args) == 2:
                "git branch",
            if args[2] == "-D":
                "git branch -D head",
                "git branch -D {branch}",
                "git branch -D {branchName}",
            if args[2].startswith("--set-upstream-to="):
                if len(args) == 3:
                    "git branch --set-upstream-to={currentBranch}",
                    "git branch --set-upstream-to=origin/main",
                elif len(args) == 4:
                    "git branch --set-upstream-to=origin/main head",
        elif command == "checkout":
            if args[2] == "-b":
                "git checkout -b head",
                "git checkout -b {newBranch}",
                "git checkout -b {newBranch} {self.branchManager.getCommitForBranch(currentBranch)}",
            if len(args) == 3:
                "git checkout {branchName}",
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
            "git rev-parse --abbrev-ref HEAD",
            "git rev-parse --short {reference}",
        elif command == "show":
            dataFormat = args[-1].split("%")[-1]
            if dataFormat == "ci":
                "git show --no-patch --no-notes {commitHash} --pretty=format:%ci",
            elif dataFormat == "ce":
                "git show --no-patch --no-notes {commitHash} --format=%ce",
                "git show --no-patch --no-notes {reference} --format=%ce",
        elif command == "status":
            "git status -s",
            "git status -s",
