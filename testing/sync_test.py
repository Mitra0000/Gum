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

import os
import subprocess
import tempfile
import unittest

from integration import IntegrationTest

# Integration tests for the `gm sync` command.
class SyncTest(IntegrationTest):

    def testSyncSingleLinearOwnedBranch(self):
        self.createFile("hello.txt", "hello world")
        self.runCommand(f"{self.GUM} add")
        self.runCommand(f"{self.GUM} commit -m 'first_commit'")
        self.runCommand("git fetch --all")
        self.runCommand("git branch --set-upstream-to=origin/master")

        self.useRemoteRepository()
        self.modifyFile("test.txt", "This is data from remote.")
        self.runCommand("git add -A")
        self.runCommand("git commit -m 'Update_test.txt'")

        self.useLocalRepository()
        self.runCommand(f"git pull --rebase")
        contents = self.readFile("test.txt")
        self.runCommand(f"{self.GUM} xl")
        self.assertEqual("This is data from remote.", contents)

if __name__ == '__main__':
    unittest.main()