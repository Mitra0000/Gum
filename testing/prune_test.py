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

import unittest

from integration import IntegrationTest


# Integration tests for the `gm prune` command.
class PruneTest(IntegrationTest):

    def testPruneOnHeadFails(self):
        self.runCommand("git checkout -b branch")
        commit = self.runCommand("git rev-parse head")
        self.runCommand(f"{self.GUM} prune {commit}")
        branches = self.runCommand("git branch").split("\n")
        hasHead = False
        for branch in branches:
            if branch == "  head":
                hasHead = True
        self.assertTrue(hasHead)

    def testPruneOnCurrentBranchFails(self):
        self.modifyFile("test.txt", "This has been modified")
        self.runCommand(f"{self.GUM} commit -m 'new_commit'")
        commit = self.runCommand("git rev-parse HEAD")
        self.runCommand(f"{self.GUM} prune {commit}")
        self.assertEqual(commit, self.runCommand("git rev-parse HEAD"))

    def testPruneOnNonExistentCommitFails(self):
        self.modifyFile("test.txt", "This has been modified")
        self.runCommand(f"{self.GUM} commit -m 'new_commit'")
        self.runCommand("git checkout head")
        self.runCommand(f"{self.GUM} prune zzzzzzz")
        # Check that there are still two branches.
        self.assertEqual(2, len(self.runCommand("git branch")[:-1].split("\n")))

    def testPruneRemovesCommit(self):
        self.modifyFile("test.txt", "This has been modified")
        self.runCommand(f"{self.GUM} commit -m 'new_commit'")
        self.runCommand("git checkout head")

        headCommit = self.runCommand("git rev-parse head")[:-1]
        allCommits = self.runCommand("git rev-parse --branches=*")[:-1].split(
            "\n")
        commitToPrune = None
        self.assertEqual(len(allCommits), 2)
        for commit in allCommits:
            if commit != headCommit:
                commitToPrune = commit
                break
        self.runCommand(f"{self.GUM} prune {commitToPrune}")
        self.assertEqual(self.runCommand("git branch"), "* head\n")

    def testPruningAllChildrenRemovesUnownedParent(self):
        self.createFile("old.txt", "This is an old file")
        self.runCommand("git add -A")
        self.runCommand(f"{self.GUM} commit -m 'old_commit'")

        self.useRemoteRepository()
        self.createFile("remote.txt", "This is a file from remote.")
        self.runCommand("git add -A")
        self.commitAsPerson("Committer", "another@committer.com",
                            "remote_commit")

        self.useLocalRepository()
        self.runCommand("git checkout head")
        self.createFile("new.txt", "This is a new file")
        self.runCommand("git add -A")
        self.runCommand(f"{self.GUM} commit -m 'new_commit'")
        self.runCommand("git branch --set-upstream-to=origin/main")
        self.runCommand("git pull --rebase")
        commitToPrune = self.runCommand("git rev-parse --short HEAD")
        parentCommit = self.runCommand("git rev-parse --short HEAD^")
        """
            We now have a tree like:
            @ 84805ab Author: You 
            | new_commit
            o 6d49ed2 Author: another@committer.com 
            | remote_commit
            | o 59c3be4 Author: You 
            |/  old_commit
            o 654cb4d Author: you@committer.com 
            | Initial_commit.
            ~
        """

        self.runCommand("git checkout head")
        self.runCommand(f"{self.GUM} prune {commitToPrune}")
        for branch in self.runCommand("git branch").split("\n"):
            if branch == "":
                continue
            self.assertNotEqual(
                parentCommit,
                self.runCommand(f"git rev-parse --short {branch}"))

    def testPruneParentRemovesChildTracking(self):
        # TODO(5): Write test and logic for this to work.
        pass


if __name__ == '__main__':
    unittest.main()
