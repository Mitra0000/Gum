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


# Integration tests for the `gm amend` command.
class AmendTest(IntegrationTest):

    def testAmendOnAuthoredCommit(self):
        originalContents = "This file will be used for amends."
        newContents = "These are new contents."
        self.createFile("amend.txt", originalContents)
        self.runCommand("git add -A")
        self.runCommand(f"{self.GUM} commit -m 'Authored_commit'")
        self.modifyFile("amend.txt", newContents)
        self.runCommand(f"{self.GUM} amend")

        # Check amend was successful.
        self.assertEqual(self.runCommand("git status --porcelain"), "")
        self.assertEqual(self.readFile("amend.txt"), newContents)

    def testAmendOnUnauthoredCommitFails(self):
        self.useRemoteRepository()
        contents = "This is data from remote."
        self.modifyFile("test.txt", contents)
        self.runCommand("git add -A")
        self.commitAsPerson("Committer", "another@committer.com",
                            "Update_test.txt")

        self.useLocalRepository()
        self.runCommand("git pull --rebase")
        newContents = "This is new data being overwritten"
        self.modifyFile("test.txt", newContents)
        self.runCommand(f"{self.GUM} amend")
        self.runCommand("git reset --hard HEAD")

        self.assertEqual(self.readFile("test.txt"), contents)


if __name__ == '__main__':
    unittest.main()
