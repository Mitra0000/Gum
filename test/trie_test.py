import unittest

import context

from test_helper import TestHelper

import trie

# Unit tests for the Trie class.
class TrieTest(unittest.TestCase):
    def setUp(self):
        self.trie = trie.Trie()
