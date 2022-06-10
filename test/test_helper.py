from test_command_runner import *

from main import *

def getParser():
    repository = MockRepository()
    commandRunner = TestCommandRunner(repository)
    return CommandParser(commandRunner)