import sys
import os

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
parent = os.path.join(parent, "src")
sys.path.append(parent)

from mock_repository import MockRepository
from util import CommandRunner

class TestCommandRunner(CommandRunner):
    def __init__(self, repository: MockRepository):
        self.repository = repository

    def run(self, command: str) -> str:
        return self.repository.processCommand(command)
    
    def runInProcess(self, command: str):
        print(self.repository.processCommand(command))