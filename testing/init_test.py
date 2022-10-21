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


# Integration tests for the `gm init` command.
class InitTest(IntegrationTest):

    def testInitCommandOnEmptyRepository(self):
        branches = self.runCommand("git branch")
        self.assertEqual(branches, "* head\n")

    def testInitCommandOnRepositoryWithBranches(self):
        self.runCommand("git checkout -b testBranch")
        self.runCommand("git checkout -b otherBranch")
        self.createFile("newfile.txt", "This is a new file.")
        self.runCommand("git add -A")
        self.runCommand("git commit -m 'Second_commit'")
        self.runCommand(f"{self.GUM} init")
        branches = self.runCommand("git branch")
        self.assertEqual(branches, "* head\n")


if __name__ == '__main__':
    unittest.main()
