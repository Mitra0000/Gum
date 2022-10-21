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


# Integration tests for the `gm revert` command.
class RevertTest(IntegrationTest):

    def testChangesToOneFileAreReverted(self):
        filename = "test.txt"
        contents = self.readFile(filename)
        self.modifyFile(filename, "These are new contents.")
        self.runCommand(f"{self.GUM} revert test.txt")
        self.assertEqual(self.readFile(filename), contents)

    def testAllChangesAreReverted(self):
        foo = "foo.txt"
        bar = "bar.txt"
        contents1 = "This is foo."
        contents2 = "This is bar."
        self.createFile(foo, contents1)
        self.createFile(bar, contents2)
        self.runCommand("git add -A")
        self.runCommand("git commit -m 'Set_contents'")
        self.modifyFile(foo, "These are new contents.")
        self.modifyFile(bar, "These are new contents.")
        self.runCommand(f"{self.GUM} revert .")

        self.assertEqual(self.readFile(foo), contents1)
        self.assertEqual(self.readFile(bar), contents2)

    def testNewFileIsDeletedOnRevert(self):
        self.createFile("foo.txt", "This is foo")
        self.runCommand("git add foo.txt")
        self.runCommand(f"{self.GUM} revert")
        with self.assertRaises(Exception):
            self.readFile("foo.txt", "This should fail.")


if __name__ == '__main__':
    unittest.main()
