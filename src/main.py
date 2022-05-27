import os
import sys
import subprocess
from xl import *

from format import *

def runCommand(command: str) -> str:
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    return out.decode("utf-8")

def buildTreeFromCommits(parentsToCommits, commits):
    commitList = list(commits)
    nodes = [Node(i) for i in commitList]
    for i in parentsToCommits.values():
        for j in i:
            commits.remove(j)
    # Commits now contains the root(s)
    for i in parentsToCommits:
        nodes[commitList.index(i)].children.extend([nodes[commitList.index(j)] for j in parentsToCommits[i]])
    return nodes[commitList.index(commits.pop())]

def getCommitFor(reference: str) -> str:
    return runCommand("git rev-parse --short " + reference)[2:-3]

def main():
    command = sys.argv[1]
    if command == "commit":
        output = "\n\n\n\nGUM: Enter a commit message. Lines beginning with 'GUM:' are removed.\nGUM: Leave commit message empty to cancel.\nGUM: --\nGUM: user: "
        output += runCommand("git config user.email") + "\n"
        output += "GUM: branch = " + runCommand("git branch --show-current")
        files = runCommand("git status -s").split("\n")
        for line in files:
            if line == "" or line.startswith("?"):
                continue
            if line.startswith("A"):
                output += "GUM: Added " + line[2:]
            elif line.startswith("M"):
                output += "GUM: Modified " + line[2:]
            elif line.startswith("D"):
                output += "GUM: Deleted " + line[2:]
        filePath = "" #os.path.realpath(__file__)
        if "\\" in filePath:
            filePath += os.path.realpath(__file__)
            filePath = "\\".join(filePath.split("\\")[:-1])
            filePath += "\\tmp\\gum_commit_message.txt"
        else:
            #filePath = "/".join(filePath.split("/")[:-1])
            filePath += "/tmp/gum_commit_message.txt"

        with open(filePath, "w") as f:
            f.write(output)

        os.system("nano " + filePath)
        commitMessage = []
        with open(filePath, "r") as f:
            content = f.read()
            lines = f.readlines()
        #if content == output:
        #    return
        print(lines)
        for line in lines:
            if line.startswith("GUM:") or line == ""  or line == "\n":
                continue
            commitMessage.append(line)
        print(commitMessage)
        currentBranch = runCommand("git branch --show-current")
        newBranch = "temp"
        runCommand("git checkout -b " + newBranch)
        runCommand("git branch --set-upstream-to=" + currentBranch)
        runCommand("git add")
        runCommand("git commit -m \"" + "\n".join(commitMessage) + "\"")
        # Store the current branch name as x
        # Create a new branch called y
        # Set upstream of y to x
        # Add known changes to y
        # Commit with commitMessage to y
        # runCommand("git commit -m " + "\n".join(commitMessage))
        #if os.path.exists(filePath):
        #    os.remove(filePath)

    elif command == "uc":
        os.system("git push")
    elif command == "status":
       out = runCommand("git status -s")
       print(format(out, bold=True, color=Color.Green))
    elif command == "xl":
        out = runCommand("git branch")[2:-1]
        currentBranch = ""
        commitToBranch = {}
        commits = set()
        parentsToCommits = {}
        for i in out.split("\\n"):
            if i == "":
                continue
            branch = i[2:]
            if i.startswith("*"):
                currentBranch = branch
            commit = getCommitFor(branch)
            commits.add(commit)
            parent = getCommitFor(branch + "^")
            commits.add(parent)
            if parent not in parentsToCommits:
                parentsToCommits[parent] = []
            parentsToCommits[parent].append(commit)
            commitToBranch[commit] = branch
        tree = buildTreeFromCommits(parentsToCommits, commits)
        xl(tree, getCommitFor(currentBranch))

    else:
        print("Unknown gum command")

if __name__ == '__main__':
    main()
