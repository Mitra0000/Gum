# Copyright 2023 The Gum Authors
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

import subprocess

from cl import CL
from xanthan import Xanthan

class ChromiumGerrit(Xanthan):
    def __init__(self):
        self._branchesToCLs: dict[str, CL] = {}
        self._initGitCl()
    
    def _updateState(self):
        self._branchesToCLs = {}
        output = self._runGitCommand("git cl status --no-branch-color")
        output = output.split("\n")[1:]
        for i in range(len(output)):
            if output[i] == "":
                break

            data = output[i].strip()
            if data.startswith("*"):
                data = data[2:]
            data = data.split()
            self._branchesToCLs[data[0]] = CL(data[2], data[3][1:-1])
        
    # Override
    # Nullable
    def getCLForBranch(self, branchName: str) -> CL:
        self._updateState()
        return self._branchesToCLs[branchName]

    # Override
    def uploadChanges(self) -> None:
        self._runGitCommand("git cl upload -T")
        
    def _runGitCommand(self, command: str):
        process = subprocess.Popen(command.split(),
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        out, _ = process.communicate()
        return out.decode("utf-8")