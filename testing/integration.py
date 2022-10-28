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
    TEST_REPOSITORY = os.path.join(tempfile.gettempdir(), "gumtesting",
                                   "sandbox", "repository")
    REMOTE_REPOSITORY = os.path.join(tempfile.gettempdir(), "gumtesting",
                                     "sandbox", "remote")
    REMOVE_WHEN_DONE = os.path.join(tempfile.gettempdir(), "gumtesting")
    GUM = "python3 " + os.path.join(
        os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "src",
        "main.py ")

    _currentRepository = TEST_REPOSITORY

    def setUp(self):
        os.makedirs(self.REMOTE_REPOSITORY)
        self.useRemoteRepository()
        self.runCommandReturnError("git init -b main")
        self.createFile("test.txt", "This is a test.")
        self.runCommand("git add -A")
        self.runCommand("git commit -m 'Initial_commit.'")
        self._currentRepository = self.REMOVE_WHEN_DONE
        self.runCommandReturnError(
            f"git clone {os.path.join(self.REMOTE_REPOSITORY, '.git')} {self.TEST_REPOSITORY}"
        )
        self.assertTrue(os.path.exists(self.TEST_REPOSITORY))
        self.useLocalRepository()
        self.runCommand(f"{self.GUM} init")

    def tearDown(self):
        shutil.rmtree(self.REMOVE_WHEN_DONE)

    def useLocalRepository(self):
        self._currentRepository = self.TEST_REPOSITORY

    def useRemoteRepository(self):
        self._currentRepository = self.REMOTE_REPOSITORY

    # Sanity tests.
    def testRepository(self):
        self.assertTrue(os.path.exists(self.TEST_REPOSITORY))

    def testRemote(self):
        self.assertTrue(os.path.exists(self.REMOTE_REPOSITORY))

    # Util functions for other tests.
    def runCommand(self, command: str) -> str:
        process = subprocess.Popen(command,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   cwd=self._currentRepository,
                                   shell=True)
        out, err = process.communicate()
        process.wait()
        return out.decode("utf-8")

    def runCommandReturnError(self, command: str) -> str:
        process = subprocess.Popen(command.split(),
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   cwd=self._currentRepository)
        out, err = process.communicate()
        process.wait()
        return err.decode("utf-8")

    def createFirstCommit(self):
        self.runCommand(f"{self.GUM} init")
        self.createFile("test.txt", "This is a test.")
        self.runCommand("git add -A")
        self.runCommand("git commit -m 'Initial_commit.'")

    def createFile(self, filename: str, contents: str):
        if os.path.exists(os.path.join(self._currentRepository, filename)):
            raise Exception("Filename already exists.")
        with open(os.path.join(self._currentRepository, filename), "w") as f:
            f.write(contents)

    def modifyFile(self, filename: str, contents: str):
        if not os.path.exists(os.path.join(self._currentRepository, filename)):
            raise Exception("Filename doesn't exist.")
        with open(os.path.join(self._currentRepository, filename), "w") as f:
            f.write(contents)

    def readFile(self, filename: str):
        if not os.path.exists(os.path.join(self._currentRepository, filename)):
            raise Exception("Filename doesn't exist.")
        with open(os.path.join(self._currentRepository, filename), "r") as f:
            return f.read()

    def commitAsPerson(self, name: str, email: str, commitMessage: str):
        originalName = self.runCommand("git config --global user.name")[:-1]
        originalEmail = self.runCommand("git config --global user.email")[:-1]
        self.runCommand(f"git config --global user.name \"{name}\"")
        self.runCommand(f"git config --global user.email \"{email}\"")
        self.runCommand(f"git commit -m \"{commitMessage}\"")
        self.runCommand(f"git config --global user.name \"{originalName}\"")
        self.runCommand(f"git config --global user.email \"{originalEmail}\"")

    def decodeFormattedText(self, text: str) -> str:
        return re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])').sub(
            '', text)


if __name__ == '__main__':
    unittest.main()
