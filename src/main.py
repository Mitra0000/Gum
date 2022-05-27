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
        output = "\n\n\n\nGUM: Enter a commit message. Lines beginning with 'GUM:' are removed.\nLeave commit message empty to cancel.\nGUM: --\nGUM: user: "
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
        file_path = os.path.realpath(__file__)
        if "\\" in file_path:
            file_path = "\\".join(file_path.split("\\")[:-1])
            file_path += "\\tmp\\commit_message.txt"
        else:
            file_path = "/".join(file_path.split("/")[:-1])
            file_path += "/tmp/commit_message.txt"

        with open(file_path, "w") as f:
            f.write(output)
        runCommand("nano " + file_path)

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
