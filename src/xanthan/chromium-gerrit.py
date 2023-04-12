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

import importlib.util
import os
import subprocess
import sys

from cl import CL
from xanthan import Xanthan

class ChromiumGerrit(Xanthan):
    def __init__(self):
        self._branchesToCLs: dict[str, CL] = {}
        self._initGitCl()
    
    def _updateState():
        pass
        
    # Override
    # Nullable
    def getUrlForBranch(self, branchName: str) -> CL:
        print(self._git_cl.get_cl_statuses([branchName], True))
        self._runGitCommand("git cl status --no-branch-color --field=url")[:-1]

    # Override
    def uploadChanges(self) -> None:
        pass
        
    def _runGitCommand(self, command: str):
        process = subprocess.Popen(command.split(),
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        out, _ = process.communicate()
        return out.decode("utf-8")
    
    def _initGitCl(self):
        """
            Performs some basic reflection to access the methods inside depot 
            tools' git_cl.py.
        """
        path = os.path.join(os.getcwd(), "third_party", "depot_tools", "git_cl.py")
        spec = importlib.util.spec_from_file_location("git_cl", path)
        self._git_cl = importlib.util.module_from_spec(spec)
        sys.modules["git_cl"] = self._git_cl
        spec.loader.exec_module(self._git_cl)