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

# Integration tests for the `gm update` command.
class UpdateTest(IntegrationTest):
    def testUpdateSwitchesBetweenCommits(self):
        self.assertEqual(self.runCommand("git rev-parse --abbrev-ref HEAD"), "head\n")

        # Create two commit branches: foo and bar.
        self.runCommand("git checkout -b foo")
        self.createFile("foo.txt", "foo")
        self.runCommand("git commit -m 'foo'")
        foo_hash = self.runCommand("git rev-parse HEAD")
        self.runCommand("git checkout -b bar")
        self.createFile("bar.txt", "bar")
        self.runCommand("git commit -m 'bar'")
        bar_hash = self.runCommand("git rev-parse HEAD")
        self.runCommand("git checkout head")

        self.runCommand(f"{self.GUM} update {foo_hash}")
        self.assertEqual(self.runCommand("git rev-parse HEAD"), foo_hash)
        self.runCommand(f"{self.GUM} update {bar_hash}")
        self.assertEqual(self.runCommand("git rev-parse HEAD"), bar_hash)

    def testWontUpdateWithUncommittedChanges(self):
        self.runCommand("git checkout -b foo")
        self.createFile("foo.txt", "foo")
        self.runCommand("git commit -m 'foo'")
        foo_hash = self.runCommand("git rev-parse HEAD")
        self.createFile("bar.txt", "bar")
        self.runCommand(f"{self.GUM} update head")
        self.assertEqual(self.runCommand("git rev-parse HEAD"), foo_hash)

if __name__ == '__main__':
    unittest.main()