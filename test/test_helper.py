import context

from mock_repository import MockRepository
from runner import CommandRunner as runner
from test_command_runner import TestCommandRunner

import main

class TestHelper:
    def __init__(self):
        self.resetRepository()
    
    def resetRepository(self):
        self.repository = MockRepository()
        self.commandRunner = TestCommandRunner(self.repository)
        runner.swapInstanceForTesting(self.commandRunner)
    
    def addChanges(self, changes):
        self.repository.addChanges(changes)
    
    def getHashForBranch(self, branchName):
        return self.repository.commitTree.branchesToCommits[branchName].commitHash