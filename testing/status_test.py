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


# Integration tests for the `gm status` command.
class StatusTest(IntegrationTest):

    def testEmptyStatusShowsNothing(self):
        status = self.runCommand(f"{self.GUM} status")
        self.assertEqual(status, "")

    def testNewFileShowsUntracked(self):
        filename = "untracked_file.txt"
        self.createFile(filename, "This is an untracked file.")
        status = self.runCommand(f"{self.GUM} status")
        status = self.decodeFormattedText(status)
        self.assertEqual(status, f"? {filename}\n")

    def testAddedFileShowsAdded(self):
        filename = "added_file.txt"
        self.createFile(filename, "This is an added file.")
        self.runCommand("git add -A")
        status = self.runCommand(f"{self.GUM} status")
        status = self.decodeFormattedText(status)
        self.assertEqual(status, f"A {filename}\n")

    def testDeletedFileShowsDeleted(self):
        filename = "test.txt"
        self.runCommand(f"rm {filename}")
        status = self.runCommand(f"{self.GUM} status")
        status = self.decodeFormattedText(status)
        self.assertEqual(status, f"D {filename}\n")

    def testModifiedFileShowsModified(self):
        filename = "test.txt"
        self.modifyFile(filename, "This file has been modified.")
        status = self.runCommand(f"{self.GUM} status")
        status = self.decodeFormattedText(status)
        self.assertEqual(status, f"M {filename}\n")

    def testMultipleStatuses(self):
        self.createFile("added_file.txt", "This is an added file.")
        self.runCommand("rm test.txt")
        status = self.runCommand(f"{self.GUM} status")
        status = self.decodeFormattedText(status)
        self.assertEqual(status, "D test.txt\n? added_file.txt\n")


if __name__ == '__main__':
    unittest.main()
