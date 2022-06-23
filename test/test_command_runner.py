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