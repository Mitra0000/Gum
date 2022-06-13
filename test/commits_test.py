import unittest

from test_helper import TestHelper

# Unit tests for the CommitManager class.
class CommitManagerTest(unittest.TestCase):
    def setup(self):
        self.helper = TestHelper()
        self.commitManager = self.helper.commitManager


