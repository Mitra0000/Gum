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
    CL_NUMBERS = "cl_numbers"
    TREE = "tree"
    TREE_HASH = "tree_hash"

    PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tmp")
    CACHE_JSON = os.path.join(PATH, "cache.json")
    
    @classmethod
    def init(cls):
        if not os.path.exists(cls.PATH):
            os.mkdir(cls.PATH)
            with open(os.path.join(cls.PATH, ".gitignore"), "w") as f:
                f.write("cache.json")
        if not os.path.exists(cls.CACHE_JSON):
            with open(cls.CACHE_JSON, "w") as f:
                json.dump({cls.CL_NUMBERS: {}, cls.TREE: {}, cls.TREE_HASH: {}}, f)

    @classmethod
    def getCachedKey(cls, key):
        if not os.path.exists(cls.CACHE_JSON):
            cls.init()
        with open(cls.CACHE_JSON, "r") as f:
            cache = json.load(f)
        return cache[key] if key in cache else None

    @classmethod
    def cacheKey(cls, key, data):
        if not os.path.exists(cls.CACHE_JSON):
            cls.init()
        with open(cls.CACHE_JSON, "r") as f:
            cache = json.load(f)
        cache[key] = data
        with open(cls.CACHE_JSON, "w") as f:
            json.dump(cache, f)
    
    @classmethod
    def invalidateKey(cls, key):
        if not os.path.exists(cls.CACHE_JSON):
            cls.init()
        with open(cls.CACHE_JSON, "r") as f:
            cache = json.load(f)
        cache[key] = None
        with open(cls.CACHE_JSON, "w") as f:
            json.dump(cache, f)