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
