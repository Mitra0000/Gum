import sys
import os

from test_runner import *

from main import *
from util import *

def main():
    commandRunner = TestRunner()
    commandParser = CommandParser(commandRunner)
    commandParser.parse(["add"])

if __name__ == "__main__":
    main()