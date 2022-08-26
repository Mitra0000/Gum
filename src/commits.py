# Copyright 2022 The Gum Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import tempfile

import branches
from node import Node
from runner import CommandRunner as runner
import status
from util import *

def createCommitMessage():
    message = ["\n\n\nGUM: Enter a commit message. Lines beginning with 'GUM:' are removed.\nGUM: Leave commit message empty to cancel.\nGUM: --\nGUM: user: "]
    message.append(runner.get().run("git config user.email"))
    message.append("\n")
    files = decodeFormattedText(status.getStatus())
    if files is None:
        print("No files to commit.")
        return None
    for line in files.split("\n"):
        if line == "" or line.startswith("?"):
            continue
        if line[0] == "A":
            message.extend(["GUM: Added " + line[2:], "\n"])
        elif line[0] == "M":
            message.extend(["GUM: Modified " + line[2:], "\n"])
        elif line[0] == "D":
            message.extend(["GUM: Deleted " + line[2:], "\n"])

    filePath = os.path.join(tempfile.gettempdir(), "gum_commit_message.txt")

    output = "".join(message)
    with open(filePath, "w") as f:
        f.write(output)

    editor = os.getenv("EDITOR")
    if editor is not None:
        runner.get().runInProcess(f"{editor} {filePath}") 
    else:
        runner.get().runInProcess(f"nano {filePath}")

    commitMessage = []
    with open(filePath, "r") as f:
        content = f.read()

    if content == output:
        return None

    lines = content.split("\n")
    for line in lines:
        if line.startswith("GUM:") or line == ""  or line == "\n":
            continue
        commitMessage.append(line)
    
    if os.path.exists(filePath):
        os.remove(filePath)
    commitMessage[0] += "\n"
    return "\n".join(commitMessage)


def getCommitForPrefix(prefix: str) -> str:
    results = getPrefixesForCommits([branches.getCommitForBranch(b) for b in branches.getAllBranches()])
    if prefix not in results:
        return prefix
    return prefix + results[prefix]

def getSingleCommitForPrefix(prefix: str) -> str:
    trie = Trie()
    commits = runner.get().run("git rev-parse --branches=*").split("\n")
    for commit in commits:
        trie.insert(commit)
    return trie.querySingle(prefix)

def getParentOfCommit(commitHash: str) -> str:
    return branches.getCommitForBranch(commitHash + "^")

def getTitleOfCommit(commitHash: str) -> str:
    return runner.get().run(f"git log {commitHash} -1 --pretty=format:%s")

def getBranchForCommit(commitHash: str) -> str:
    foundBranch = None
    for branch in branches.getAllBranches():
        if branches.getCommitForBranch(branch).startswith(commitHash):
            if foundBranch:
                return None
            foundBranch = branch
    return foundBranch

def getFullCommitHash(reference: str) -> str:
    return runner.get().run(f"git rev-parse {reference}")


def getDateForCommit(commitHash: str) -> str:
    return "".join(runner.get().run(f"git show --no-patch --no-notes {commitHash} --pretty=format:%ci").split()[:-1])


def getEmailForCommit(commitHash: str) -> str:
    return runner.get().run(f"git show --no-patch --no-notes {commitHash} --format=%ae")[:-1]