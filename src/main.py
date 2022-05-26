import os
import sys
import subprocess
from xl import *

from format import *

def runCommand(command: str) -> str:
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    return str(out)

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
        name = sys.argv[2]
        os.system("git commit -m '" + name + "'")
    elif command == "uc":
        os.system("git push")
    elif command == "status":
       out = runCommand("git status")
       index = out.find("working directory)") + 24
       out = out[index:]
       index = out.find("\\n\\n")
       out = out[:index]
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
