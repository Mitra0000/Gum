import test_helper
from unittest import UnitTest

# Unit tests for the BranchManager class.
class CommitManagerTest(UnitTest):
    def setup(self):
        parser = test_helper.getParser()
        self.branchManager = parser.branchManager
    
    def before(self):
        pass
    
    def after(self):
        pass