from branches_test import BranchManagerTest
from commits_test import CommitManagerTest
from main_test import CommandParserTest
from trie_test import TrieTest
from util_test import UtilTest

def main():
    tests = [BranchManagerTest(), CommandParserTest(), CommitManagerTest(), TrieTest(), UtilTest()]
    for test in tests:
        test.setup()
        test.run()

if __name__ == '__main__':
    main()