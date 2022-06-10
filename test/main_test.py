import test_helper
from unittest import UnitTest

# Unit tests for the main.py file.
class CommandParserTest(UnitTest):
    def setup(self):
        self.parser = test_helper.getParser()
    
    def before(self):
        print("Test is about to run.")
    
    def after(self):
        print("Test has finished.")
    
    @UnitTest.Test
    def firstTest(self):
        print("This is the first test.")
    
    @UnitTest.Test
    def secondTest(self):
        print("This is the second test.")