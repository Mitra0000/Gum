import os
import unittest

from branches_test import BranchManagerTest
from commits_test import CommitManagerTest
from main_test import CommandParserTest
from trie_test import TrieTest
from util_test import UtilTest

def suite():
    loader = unittest.TestLoader()
    return loader.discover(os.path.dirname(os.path.realpath(__file__)), "*_test.py")

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(suite())