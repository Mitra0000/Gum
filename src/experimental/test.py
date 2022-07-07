import unittest
from node import Node

import main


# Unit tests for the BranchManager class.
class PrintTreeTest(unittest.TestCase):
    def testWith1Child(self):
        parent = Node("head", "a", None, [], False)
        child = Node("child", "b", parent, [], True)
        parent.children.append(child)

        tree = {"head": parent, "child": child}
        output = main.printTree(tree)
        self.assertEqual(output, "o child\n| \no head\n| \n~")
    
    def testWith1Grandchild(self):
        grandparent = Node("head", "a", None, [], False)
        parent = Node("parent", "b", grandparent, [], True)
        child = Node("child", "c", parent, [], True)
        grandparent.children.append(parent)
        parent.children.append(child)

        tree = {"head": grandparent, "parent": parent, "child": child}
        output = main.printTree(tree)
        self.assertEqual(output, "o child\n| \no parent\n| \no head\n| \n~")
    
    def testWith2Children(self):
        parent = Node("head", "a", None, [], False)
        child1 = Node("child1", "b", parent, [], True)
        child2 = Node("child2", "c", parent, [], True)
        parent.children.extend([child1, child2])

        tree = {"head": parent, "child1": child1, "child2": child2}
        output = main.printTree(tree)
        self.assertEqual(output, "o child2\n| \n| o child1\n|/\no head\n| \n~")
    
    def testWith3Children(self):
        parent = Node("head", "a", None, [], False)
        child1 = Node("child1", "b", parent, [], True)
        child2 = Node("child2", "c", parent, [], True)
        child3 = Node("child3", "d", parent, [], True)
        parent.children.extend([child1, child2, child3])

        tree = {"head": parent}
        output = main.printTree(tree)
        self.assertEqual(output, "o child3\n| \n|   o child2\n|  /\n| | o child1\n| |/\n|/\no head\n| \n~")

    def testWith3Children1Grandchild(self):
        parent = Node("head", "a", None, [], False)
        child1 = Node("child1", "b", parent, [], True)
        child2 = Node("child2", "c", parent, [], True)
        child3 = Node("child3", "d", parent, [], True)
        grandchild = Node("grandchild", "e", child1, [], True)
        parent.children.extend([child1, child2, child3])
        child1.children.append(grandchild)

        tree = {"head": parent}
        output = main.printTree(tree)
        print(output)
        self.assertEqual(output, "o child3\n| \n|   o child2\n|  /\n| | o grandchild\n| | | \n| | o child1\n| |/\n|/\no head\n| \n~")

if __name__ == '__main__':
    unittest.main()