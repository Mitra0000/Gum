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


# Integration tests for the `gm add` command.
class AddTest(IntegrationTest):

    def testAddCommandTracksUntrackedFile(self):
        self.createFile("added_file.txt", "This was just added.")
        status = self.runCommand("git status --porcelain")
        self.assertEqual(status, "?? added_file.txt\n")
        self.runCommand(f"{self.GUM} add")
        status = self.runCommand("git status --porcelain")
        self.assertEqual(status, "A  added_file.txt\n")

    def testAddSpecificFileDoesntAddAllFiles(self):
        self.createFile("foo.txt", "This is foo.")
        self.createFile("bar.txt", "This is bar.")
        status = self.runCommand("git status --porcelain")
        self.assertEqual(status, "?? bar.txt\n?? foo.txt\n")
        self.runCommand(f"{self.GUM} add foo.txt")
        status = self.runCommand("git status --porcelain")
        self.assertEqual(status, "A  foo.txt\n?? bar.txt\n")


if __name__ == '__main__':
    unittest.main()
