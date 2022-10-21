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


# Integration tests for the `gm forget` command.
# Should be kept reasonably up to date with add_test.py.
class ForgetTest(IntegrationTest):

    def testForgetCommandUntracksTrackedFile(self):
        self.createFile("added_file.txt", "This was just added.")
        self.runCommand("git add -A")
        self.assertEqual(self.runCommand("git status --porcelain"),
                         "A  added_file.txt\n")
        self.runCommand(f"{self.GUM} forget added_file.txt")
        status = self.runCommand("git status --porcelain")
        self.assertEqual(status, "?? added_file.txt\n")

    def testForgetSpecificFileDoesntForgetAllFiles(self):
        self.createFile("foo.txt", "This is foo.")
        self.createFile("bar.txt", "This is bar.")
        self.runCommand("git add -A")
        status = self.runCommand("git status --porcelain")
        self.assertEqual(status, "A  bar.txt\nA  foo.txt\n")
        self.runCommand(f"{self.GUM} forget foo.txt")
        status = self.runCommand("git status --porcelain")
        self.assertEqual(status, "A  bar.txt\n?? foo.txt\n")


if __name__ == '__main__':
    unittest.main()
