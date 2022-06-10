from test_helper import TestHelper
from unittest import UnitTest

# Unit tests for the CommitManager class.
class CommitManagerTest(UnitTest):
    def setup(self):
        self.helper = TestHelper()
        self.commitManager = self.helper.commitManager


