import os
import shutil
import subprocess
import unittest

import context

# Template for integration tests to inherit from.
class IntegrationTest(unittest.TestCase):
    TEST_REPOSITORY = os.path.join(os.path.dirname(os.path.realpath(__file__)), "repository")
    GUM = "python3 " + os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "src", "main.py ")
    def setUp(self):
        os.mkdir(self.TEST_REPOSITORY)
        self.runCommand("git submodule init")
        
    def tearDown(self):
        pass
        # shutil.rmtree(self.TEST_REPOSITORY)
    
    def testRepository(self):
        self.assertTrue(os.path.exists(self.TEST_REPOSITORY))

    def runCommand(self, command: str) -> str:
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.TEST_REPOSITORY)
        out, err = process.communicate()
        process.wait()
        return out.decode("utf-8")

if __name__ == '__main__':
    unittest.main()