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
from runner import CommandRunner

class TestCommandRunner(CommandRunner):
    def __init__(self, repository: MockRepository):
        self.repository = repository

    def run(self, command: str) -> str:
        return self.repository.processCommand(command)
    
    def runInProcess(self, command: str):
        print(self.repository.processCommand(command))