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

from node import Node


class LumberJack:
    trunk = set()

    @classmethod
    def getTrunk(cls, node: Node):
        best = None
        maxChildren = -1
        for child in node.children:
            if len(child.children) > maxChildren:
                maxChildren = len(child.children)
                best = child
        if best is not None:
            cls.trunk.add(best)
            best.level = 0
            cls.getTrunk(best)

    @classmethod
    def markNodes(cls, node: Node):
        if len(node.children) > 0:
            startingLevel = max(node.level, 1)
            addition = 0
            for child in node.children:
                if child not in cls.trunk:
                    child.level = startingLevel + addition
                    addition += 1
                cls.markNodes(child)
