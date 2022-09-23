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

from runner import CommandRunner as runner

class TrieNode:
    def __init__(self, char):
        self.char = char
        self.is_end = False
        self.counter = 0
        self.children = {}

class Trie(object):
    def __init__(self):
        self.root = TrieNode("")
    
    def insert(self, word):
        node = self.root

        for char in word:
            if char in node.children:
                node.children[char].counter += 1
                node = node.children[char]
            else:
                new_node = TrieNode(char)
                node.children[char] = new_node
                node = new_node
                node.counter += 1

        node.is_end = True
        
    def dfs(self, node, prefix):
        if node.counter == 1:
            self.output[prefix + node.char] = self.searchTail(list(node.children.values())[0])
            return
        
        for child in node.children.values():
            self.dfs(child, prefix + node.char)
    
    def searchTail(self, node):
        tail = node.char
        while node.children:
            if len(node.children) > 1:
                return None
            elif len(node.children) == 1:
                node = list(node.children.values())[0]
                tail += node.char
            else:
                return None
        return tail

    # Deprecated
    def query(self):
        self.output = {}
        node = self.root
        for child in node.children.values():
            self.dfs(child, "")
        return self.output
    
    def querySingle(self, query):
        node = self.root
        idx = 0
        while node.children and idx < len(query):
            if query[idx] not in node.children:
                break
            node = node.children[query[idx]]
            idx += 1
        else:
            if len(node.children) <= 1:
                tail = self.searchTail(node)
                if not tail:
                    return None
                query = query[:-1] + tail
                return runner.get().run(f"git rev-parse --short {query}")[:-1]
        return None