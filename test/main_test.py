from test_command_runner import *

from main import *
from unittest import UnitTest

# Unit tests for the main.py file.
class CommandParserTest(UnitTest):    
    def before(self):
        self.repository = MockRepository()
        commandRunner = TestCommandRunner(self.repository)
        self.parser = CommandParser(commandRunner)
