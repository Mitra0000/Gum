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
import re
import shutil
import subprocess
import tempfile
import unittest

# Template for integration tests to inherit from.
class IntegrationTest(unittest.TestCase):
    TEST_REPOSITORY = os.path.join(tempfile.gettempdir(), "gumtesting", "sandbox", "repository")
    REMOVE_WHEN_DONE = os.path.join(tempfile.gettempdir(), "gumtesting")
    GUM = "python3 " + os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "src", "main.py ")

    def setUp(self):
        os.makedirs(self.TEST_REPOSITORY)
        self.runCommand("git init")
        self.createFirstCommit()
        
    def tearDown(self):
        shutil.rmtree(self.REMOVE_WHEN_DONE)
    
    def testRepository(self):
        self.assertTrue(os.path.exists(self.TEST_REPOSITORY))

    def runCommand(self, command: str) -> str:
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.TEST_REPOSITORY)
        out, err = process.communicate()
        process.wait()
        return out.decode("utf-8")

    def runCommandReturnError(self, command: str) -> str:
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.TEST_REPOSITORY)
        out, err = process.communicate()
        process.wait()
        return err.decode("utf-8")

    def createFirstCommit(self):
        self.runCommand(f"{self.GUM} init")
        self.createFile("test.txt", "This is a test.")
        self.runCommand("git add -A")
        self.runCommand("git commit -m 'Initial_commit.'")
    
    def createFile(self, filename: str, contents: str):
        if os.path.exists(os.path.join(self.TEST_REPOSITORY, filename)):
            raise Exception("Filename already exists.")
        with open(os.path.join(self.TEST_REPOSITORY, filename), "w") as f:
            f.write(contents)
    
    def modifyFile(self, filename: str, contents: str):
        if not os.path.exists(os.path.join(self.TEST_REPOSITORY, filename)):
            raise Exception("Filename doesn't exist.")
        with open(os.path.join(self.TEST_REPOSITORY, filename), "w") as f:
            f.write(contents)
    
    def decodeFormattedText(self, text: str) -> str:
        return re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])').sub('', text)

if __name__ == '__main__':
    unittest.main()