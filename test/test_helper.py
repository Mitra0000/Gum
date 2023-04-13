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

import context

from mock_repository import MockRepository
from test_command_runner import TestCommandRunner

import main
from runner import CommandRunner as runner


class TestHelper:

    def __init__(self):
        self.resetRepository()

    def resetRepository(self):
        self.repository = MockRepository()
        self.commandRunner = TestCommandRunner(self.repository)
        runner.swapInstance(self.commandRunner)

    def addChanges(self, changes):
        self.repository.addChanges(changes)

    def getHashForBranch(self, branchName):
        return self.repository.commitTree.branchesToCommits[
            branchName].commitHash
