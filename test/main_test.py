import unittest

import context

from test_helper import TestHelper

import main

# Unit tests for the main.py file.
class CommandParserTest(unittest.TestCase):    
    def before(self):
        self.helper = TestHelper()
