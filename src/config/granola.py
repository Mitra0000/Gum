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

import sys

from repository.node import Node


class Granola:
    """
        A simple binary serializer designed to quickly cache and retrieve the 
        tree object.

        Strings are stored as a single byte for length followed by a byte for 
        each character.
        The commit hash is converted from hex and is stored as an integer.
        The parent is stored as a branch name (string).
        The children are stored as a series of branch names with a preceding 
        length byte.
        The prefix, suffix and is_owned attributes are compressed into a single 
        byte with the first bit indicating whether the branch is owned and the 
        remaining bits indicating the index of the prefix/suffix split.
    """

    @classmethod
    def serialize(cls, tree):
        buffer = bytearray()
        for branch in tree:
            buffer += cls.serializeNode(tree[branch])
        return buffer

    @classmethod
    def deserialize(cls, treeBytes):
        it = 0
        tree = {}
        while it < len(treeBytes):
            newNode, it = cls.deserializeNode(treeBytes, it)
            tree[newNode.branch] = newNode
        return cls._updateRefs(tree)

    @classmethod
    def serializeNode(cls, node):
        branch = cls._createVarLengthBytes(node.branch)
        commit = bytearray.fromhex(node.commit.zfill(40))
        parent = cls._createVarLengthBytes(
            node.parent.branch) if node.parent else bytearray(1)
        children = bytearray([len(node.children)] * 1)
        for child in node.children:
            children += cls._createVarLengthBytes(child.branch)
        extra = ((node.is_owned << 7) | len(node.commitPrefix)).to_bytes(
            1, byteorder=sys.byteorder)
        return branch + commit + parent + children + extra

    @classmethod
    def deserializeNode(cls, treeBytes, it):
        branch, it = cls._readVarLengthBytes(treeBytes, it, str)
        commit = treeBytes[it:it + 20].hex().lstrip("0")
        it += 20
        if treeBytes[it] == 0:
            it += 1
            parent = None
        else:
            parent, it = cls._readVarLengthBytes(treeBytes, it, str)
        numChildren = treeBytes[it]
        children = []
        it += 1
        for i in range(numChildren):
            child, it = cls._readVarLengthBytes(treeBytes, it, str)
            children.append(child)
        extra = treeBytes[it]
        isOwned = (extra >> 7 & 1) == 1
        lenPrefix = extra & ((1 << 7) - 1)
        prefix = commit[:lenPrefix]
        suffix = commit[lenPrefix:]
        return Node(branch, commit, parent, children, isOwned, prefix,
                    suffix), it + 1

    @classmethod
    def _updateRefs(cls, tree):
        for branch in tree:
            if tree[branch].parent:
                tree[branch].parent = tree[tree[branch].parent]
            for i in range(len(tree[branch].children)):
                tree[branch].children[i] = tree[tree[branch].children[i]]
        return tree

    @classmethod
    def _createVarLengthBytes(cls, obj):
        result = bytearray(1 + len(obj))
        result[0] = len(obj)
        result[1:] = bytes(obj,
                           encoding="utf-8") if type(obj) is str else bytes(obj)
        return result

    @classmethod
    def _readVarLengthBytes(cls, bytearr, it, datatype):
        byteslength = bytearr[it]
        it += 1
        if datatype is str:
            return bytearr[it:it +
                           byteslength].decode("utf-8"), it + byteslength


if __name__ == "__main__":
    aaaco = Node("aaaco", "e2eef0550c875", "head", [], True, "e",
                 "2eef0550c875")
    aaacp = Node("aaacp", "6251eb01da4bf", "head", [], True, "6",
                 "251eb01da4bf")
    aaagd = Node("aaagd", "1c907c173b34f", "majt", [], True, "1c",
                 "907c173b34f")
    head = Node("head", "109ce5f58168f", None,
                ['78a1707b88615', '6251eb01da4bf', 'e2eef0550c875'], False,
                "10", "9ce5f58168f")
    majt = Node("majt", "78a1707b88615", "head", ['1c907c173b34f'], False, "7",
                "8a1707b88615")
    aaaco.parent = head
    aaacp.parent = head
    aaagd.parent = majt
    majt.parent = head
    head.children[0] = aaagd
    head.children[1] = aaacp
    head.children[2] = aaaco
    majt.children[0] = aaagd

    tree = {
        "aaaco": aaaco,
        "aaacp": aaacp,
        "aaagd": aaagd,
        "head": head,
        "majt": majt
    }

    result = Granola.serialize(tree)
    newResult = Granola.deserialize(result)
    for i in newResult:
        assert str(newResult[i]) == str(tree[i]), "\n" + str(
            newResult[i]) + " is not equal to \n" + str(tree[i])
