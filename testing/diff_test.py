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

# Integration tests for the `gm diff` command.
class DiffTest(IntegrationTest):
    def testEmptyDiff(self):
        self.assertEqual(self.runCommand(f"{self.GUM} diff"), "")
        self.assertGumOutputEqualsGitOutput()

    def testAddedDiff(self):
        self.createFile("newfile.txt", "This is a new file.")
        self.assertGumOutputEqualsGitOutput()

    def testModifiedDiff(self):
        self.modifyFile("test.txt", "This is a modified test.")
        self.assertGumOutputEqualsGitOutput()

    def testDeletedDiff(self):
        self.modifyFile("test.txt", "")
        self.assertGumOutputEqualsGitOutput()

    def testMultiFileDiff(self):
        self.modifyFile("test.txt", "This is a modified test.")
        self.createFile("newfile.txt", "This is a new file.")
        self.assertGumOutputEqualsGitOutput()

    def assertGumOutputEqualsGitOutput(self):
        gumOutput = self.runCommand(f"{self.GUM} diff")
        gitOutput = self.runCommand("git diff")
        self.assertEqual(gumOutput, gitOutput)

if __name__ == '__main__':
    unittest.main()