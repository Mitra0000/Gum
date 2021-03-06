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

class CommandRunner:
    _instance = None

    @classmethod
    def get(cls):
        if cls._instance is None:
            cls._instance = CommandRunner()
        return cls._instance

    @classmethod
    def swapInstanceForTesting(cls, instance):
        cls._instance = instance

    def run(self, command: str) -> str:
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        return out.decode("utf-8")
    
    def runInProcess(self, command: str):
        os.system(command)