import sys
import os

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
parent = os.path.join(parent, "src")
sys.path.append(parent)

from util import CommandRunner

class TestRunner(CommandRunner):
    def run(self, command: str) -> str:
        print(command)
    
    def runInProcess(self, command: str):
        print("In process", command)