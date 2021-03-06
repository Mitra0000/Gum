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

import fnmatch
import unittest

from integration import IntegrationTest

# Integration tests for the `gm xl` command.
class XlTest(IntegrationTest):
    def testXlOnEmptyRepository(self):
        output = self.runCommand(f"{self.GUM} xl")
        output = self.decodeFormattedText(output)
        self.assertTrue(fnmatch.fnmatch(output, "@ * Author: You \n| 'Initial_commit.'\n~\n"))

    def testXlOnTwoLinearCommits(self):
        self.runCommand("git checkout -b newBranch")
        self.runCommand("git branch --set-upstream-to=head")
        self.createFile("newfile.txt", "This is a new file.")
        self.runCommand("git add -A")
        self.runCommand("git commit -m 'Child_commit'")

        output = self.runCommand(f"{self.GUM} xl")
        output = self.decodeFormattedText(output)
        self.assertTrue(fnmatch.fnmatch(output, "@ * Author: You \n| 'Child_commit'\no * Author: You \n| 'Initial_commit.'\n~\n"))

    def testXlOnParentWithTwoChildren(self):
        self.runCommand("git checkout -b firstChild")
        self.runCommand("git branch --set-upstream-to=head")
        self.createFile("newfile.txt", "This is a new file.")
        self.runCommand("git add -A")
        self.runCommand("git commit -m 'First_child_commit'")

        self.runCommand("git checkout head")
        self.runCommand("git checkout -b secondChild")
        self.runCommand("git branch --set-upstream-to=head")
        self.createFile("different_file.txt", "This is a different file.")
        self.runCommand("git add -A")
        self.runCommand("git commit -m 'Second_child_commit'")

        output = self.runCommand(f"{self.GUM} xl")
        output = self.decodeFormattedText(output)
        self.assertTrue(fnmatch.fnmatch(output, "o * Author: You \n| 'First_child_commit'\n| @ * Author: You \n|/  'Second_child_commit'\no * Author: You \n| 'Initial_commit.'\n~\n")
                        or fnmatch.fnmatch(output, "@ * Author: You \n| 'Second_child_commit'\n| o * Author: You \n|/  'First_child_commit'\no * Author: You \n| 'Initial_commit.'\n~\n"))

if __name__ == '__main__':
    unittest.main()