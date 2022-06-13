from test_command_runner import *

from main import *

class TestHelper:
    def __init__(self):
        self.resetRepository()
    
    def resetRepository(self):
        self.repository = MockRepository()
        self.commandRunner = TestCommandRunner(self.repository)
        self.parser = CommandParser(self.commandRunner)
        self.commitManager = self.parser.commitManager
        self.branchManager = self.parser.branchManager
    
    def addChanges(self, changes):
        self.repository.addChanges(changes)
    
    def getHashForBranch(self, branchName):
        return self.repository.commitTree.branchesToCommits[branchName].commitHash
