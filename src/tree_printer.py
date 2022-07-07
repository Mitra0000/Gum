import branches
from cacher import Cacher
import commits
from util import *

class TreePrinter:
    _output = []

    @classmethod
    def print(cls, root):
        cls._output = []
        cls._currentBranch = branches.getCurrentBranch()
        cls._clNumbers = Cacher.getCachedClNumbers()
        if len(cls._clNumbers) == 0:
            cls._clNumbers = branches.getUrlsForBranches()
        cls._output.append("~")
        cls._appendNode(root, "| ", "")
        if cls._output[1] == "|":
            del cls._output[1]
        while cls._output:
            print(cls._output.pop())
    
    @classmethod
    def _appendNode(cls, node, bP, tP):
        cls._output.append(bP + commits.getTitleOfCommit(node.commit))
        cls._output.append("".join([tP, "@ " if cls._currentBranch == node.branch else "o ", formatText(node.commitPrefix, underline = True, color = Color.Yellow), formatText(node.commitSuffix, color = Color.Yellow), formatText(" Author: ", color=Color.Blue), "You" if node.is_owned else commits.getEmailForCommit(node.commit), " ", cls._clNumbers[node.commit] if node.commit in cls._clNumbers and cls._clNumbers[node.commit] != "None" else ""]))
        if len(node.children) == 1:
            cls._appendNode(node.children[0], tP + "| ", tP)
        elif len(node.children) == 2:
            cls._appendNode(node.children[0], bP[:-2] + "|/  ", tP + "| ")
            cls._appendNode(node.children[1], bP, tP)
        elif len(node.children) > 2:
            cls._output.append(bP[:-2] + "|/")
            for child in node.children[:-2]:
                cls._appendNode(child, bP + "|/", tP + "| | ")
            cls._appendNode(node.children[-2], bP + " /", tP + "|   ")
            cls._appendNode(node.children[-1], bP, tP)