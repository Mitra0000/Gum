import test_helper
from unittest import UnitTest

# Unit tests for the CommitManager class.
class CommitManagerTest(UnitTest):
    def setup(self):
        parser = test_helper.getParser()
        self.commitManager = parser.commitManager
    
    def before(self):
        pass
    
    def after(self):
        pass