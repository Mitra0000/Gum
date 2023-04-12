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

import context

from config.cacher import Cacher


class CacherForTesting(Cacher):

    def __init__(self):
        self._cache = {
            Cacher.CL_NUMBERS: {},
            Cacher.TREE: {},
            Cacher.TREE_HASH: {},
            Cacher.NEXT_BRANCH: "aaaaa"
        }

    def _init(self):
        self._cache = {
            Cacher.CL_NUMBERS: {},
            Cacher.TREE: {},
            Cacher.TREE_HASH: {},
            Cacher.NEXT_BRANCH: "aaaaa"
        }

    def _getCachedKey(self, key: str):
        """
            Returns the value associated with a given key or None if it doens't 
            exist in the cache.
        """
        return self._cache[key] if key in self._cache else None

    def _cacheKey(self, key: str, data):
        """ Stores the given data along with its key in the cache. """
        self._cache[key] = data

    def _invalidateKey(self, key: str):
        """ Deletes any data associated with the given key. """
        self._cache[key] = None
