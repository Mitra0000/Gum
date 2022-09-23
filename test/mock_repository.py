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

import context

from node import Node

OWNED_EMAIL = "user@example.com"
ANOTHER_EMAIL = "someone.else@example.com"

class MockRepository:
    def __init__(self):
        self.tree = {"head": Node("head", "0", None, [], False, "0", "")}
        self.nextBranch = 1
        self.currentBranch = "head"
    
    def createNewBranch(self, name):
        commit = str(self.nextBranch)
        self.createNewBranch(name, commit)
    
    def createNewBranch(self, name, commit):
        self.tree[name] = Node(name, commit, self.tree[self.currentBranch], [], True, commit, "")
        self.tree[self.currentBranch].children.append(self.tree[name])
    
    def setCurrentBranch(self, branchName):
        assert branchName in self.tree, f"Couldn't find branch {branchName}"
        self.currentBranch = branchName
    
    def removeBranch(self, branchName):
        assert branchName in self.tree, f"Couldn't find branch {branchName}"
        for child in self.tree[branchName].children:
            self.removeBranch(child)
        if self.tree[branchName].parent:
            self.tree[branchName].parent.children.remove(self.tree[branchName])
        del self.tree[branchName]
    
    def processCommand(self, command):
        # Commands for branches.py
        if command == "git branch":
            result = ""
            for branch in self.tree:
                result += "* " if branch == self.currentBranch else "  "
                result += branch + "\n"
            return result
        elif command == "git rev-parse --abbrev-ref HEAD":
            return self.currentBranch + "\n"
        elif command.startswith("git rev-parse --short"):
            branch = command.split()[-1]
            if branch in self.tree:
                return self.tree[branch].commit + "\n"
            return branch + "\n"
        elif command.startswith("git show --no-patch --no-notes"):
            branch = command.split()[4]
            return (OWNED_EMAIL if self.tree[branch].is_owned else ANOTHER_EMAIL) + "\n"
        elif command == "git config user.email":
            return OWNED_EMAIL + "\n"
        # Commands for commits.py
        elif command == "git rev-parse --branches=*":
            s = ""
            for branch in self.tree:
                s += self.tree[branch].commit + "\n"
            return s