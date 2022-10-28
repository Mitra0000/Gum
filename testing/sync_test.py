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
import subprocess
import tempfile
import unittest

from integration import IntegrationTest


# Integration tests for the `gm sync` command.
class SyncTest(IntegrationTest):

    def testSyncSingleLinearOwnedBranch(self):
        self.createFile("hello.txt", "hello world")
        self.runCommand(f"{self.GUM} add")
        self.runCommand(f"{self.GUM} commit -m 'first_commit'")
        self.runCommand("git fetch --all")
        self.runCommand("git branch --set-upstream-to=origin/main")

        self.useRemoteRepository()
        newContents = "This is data from remote."
        self.modifyFile("test.txt", newContents)
        self.runCommand("git add -A")
        self.commitAsPerson("Committer", "another@committer.com",
                            "Update_test.txt")

        self.useLocalRepository()
        self.runCommand(f"{self.GUM} sync")
        contents = self.readFile("test.txt")
        self.assertEqual(newContents, contents)

        commits = self.runCommand("git log -2 --pretty=oneline").split("\n")
        self.assertTrue(commits[0].endswith("first_commit"))
        self.assertTrue(commits[1].endswith("Update_test.txt"))

    def commitAsPerson(self, name: str, email: str, commitMessage: str):
        originalName = self.runCommand("git config --global user.name")[:-1]
        originalEmail = self.runCommand("git config --global user.email")[:-1]
        self.runCommand(f"git config --global user.name \"{name}\"")
        self.runCommand(f"git config --global user.email \"{email}\"")
        self.runCommand(f"git commit -m \"{commitMessage}\"")
        self.runCommand(f"git config --global user.name \"{originalName}\"")
        self.runCommand(f"git config --global user.email \"{originalEmail}\"")


if __name__ == '__main__':
    unittest.main()
