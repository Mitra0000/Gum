# Copyright 2022 The Gum Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
        cls._clNumbers = Cacher.getCachedKey(Cacher.CL_NUMBERS)
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
                cls._appendNode(child, bP + "|/  ", tP + "| | ")
            cls._appendNode(node.children[-2], bP + " /  ", tP + "|   ")
            cls._appendNode(node.children[-1], bP, tP)