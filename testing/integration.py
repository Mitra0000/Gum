import os
import shutil
import subprocess
import tempfile
import unittest

import context

# Template for integration tests to inherit from.
class IntegrationTest(unittest.TestCase):
    TEST_REPOSITORY = os.path.join(tempfile.gettempdir(), "gumtesting", "sandbox", "repository")
    REMOVE_WHEN_DONE = os.path.join(tempfile.gettempdir(), "gumtesting")
    GUM = "python3 " + os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "src", "main.py ")

    def setUp(self):
        os.makedirs(self.TEST_REPOSITORY)
        self.runCommand("git init")
        
    def tearDown(self):
        shutil.rmtree(self.REMOVE_WHEN_DONE)
    
    def testRepository(self):
        self.assertTrue(os.path.exists(self.TEST_REPOSITORY))

    def runCommand(self, command: str) -> str:
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.TEST_REPOSITORY)
        out, err = process.communicate()
        process.wait()
        return out.decode("utf-8")
    
    def createFirstCommit(self):
        self.runCommand(f"{self.GUM} init")
        with open(os.path.join(self.TEST_REPOSITORY, "test.txt"), "w") as f:
            f.write("This is a test.")
        self.runCommand("git add -A")
        self.runCommand("git commit -m 'Initial_commit.'")

if __name__ == '__main__':
    unittest.main()