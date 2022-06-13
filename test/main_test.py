import unittest

from test_command_runner import *

from main import *

# Unit tests for the main.py file.
class CommandParserTest(unittest.TestCase):    
    def before(self):
        self.repository = MockRepository()
        commandRunner = TestCommandRunner(self.repository)
        self.parser = CommandParser(commandRunner)
