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


# Integration tests for the `gm commit` command.
class CommitTest(IntegrationTest):

    def testCommitCreatesNewBranch(self):
        currentBranch = self.runCommand("git branch --show-current")
        self.modifyFile("test.txt", "This has been modified.")
        self.runCommand(f"{self.GUM} commit -m 'new_commit'")
        newBranch = self.runCommand("git branch --show-current")
        self.assertNotEqual(currentBranch, newBranch)

    def testCommitShowsInGitLog(self):
        self.modifyFile("test.txt", "This has been modified.")
        self.runCommand(f"{self.GUM} commit -m 'new_commit'")
        self.assertEqual(
            self.runCommand("git log --oneline").split()[1], "new_commit")


if __name__ == '__main__':
    unittest.main()
