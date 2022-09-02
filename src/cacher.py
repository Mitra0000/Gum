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

import json
import os

class Cacher:
    """
        A simple helper class to handle all interaction with a cache stored on 
        disk. A cache is required so that state can be maintained between 
        commands as each command is processed in its own execution of the 
        program.

        The cache on disk is stored as a JSON and is a key-value store where 
        the keys are strings and the values can be any serialisable type.

        Keys should be stored as static constants below to avoid spelling 
        mistakes.
    """

    CL_NUMBERS = "cl_numbers"
    TREE = "tree"
    TREE_HASH = "tree_hash"
    NEXT_BRANCH = "next_branch"

    PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tmp")
    CACHE_JSON = os.path.join(PATH, "cache.json")
    _INSTANCE = None

    @classmethod
    def init(cls) -> None:
        cls._get._init()

    @classmethod
    def getCachedKey(cls, key):
        return cls._get()._getCachedKey(key)

    @classmethod
    def cacheKey(cls, key: str, data):
        return cls._get()._cacheKey(key, data)

    @classmethod
    def invalidateKey(cls, key: str):
        return cls._get()._invalidateKey(key)

    @classmethod
    def swapInstanceForTesting(cls, testingInstance):
        cls._INSTANCE = testingInstance

    @classmethod
    def _get(cls) -> "Cacher":
        if not cls._INSTANCE:
            cls._INSTANCE = Cacher()
        return cls._INSTANCE
    
    def _init(self):
        """ Initialises the cache in the event it may have been deleted. """
        if not os.path.exists(self.PATH):
            os.mkdir(self.PATH)
            with open(os.path.join(self.PATH, ".gitignore"), "w") as f:
                f.write("cache.json")
        if not os.path.exists(self.CACHE_JSON):
            with open(self.CACHE_JSON, "w") as f:
                json.dump({self.CL_NUMBERS: {}, self.TREE: {}, self.TREE_HASH: {}, self.NEXT_BRANCH: "aaaaa"}, f)

    def _getCachedKey(self, key: str):
        """
            Returns the value associated with a given key or None if it doens't 
            exist in the cache.
        """
        if not os.path.exists(self.CACHE_JSON):
            self.init()
        with open(self.CACHE_JSON, "r") as f:
            cache = json.load(f)
        return cache[key] if key in cache else None

    def _cacheKey(self, key: str, data):
        """ Stores the given data along with its key in the cache. """
        if not os.path.exists(self.CACHE_JSON):
            self.init()
        with open(self.CACHE_JSON, "r") as f:
            cache = json.load(f)
        cache[key] = data
        with open(self.CACHE_JSON, "w") as f:
            json.dump(cache, f)
    
    def _invalidateKey(self, key: str):
        """ Deletes any data associated with the given key. """
        if not os.path.exists(self.CACHE_JSON):
            self.init()
        with open(self.CACHE_JSON, "r") as f:
            cache = json.load(f)
        cache[key] = None
        with open(self.CACHE_JSON, "w") as f:
            json.dump(cache, f)