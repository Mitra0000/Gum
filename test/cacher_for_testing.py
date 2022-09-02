import context

from cacher import Cacher

class CacherForTesting(Cacher):
    def __init__(self):
        self._cache = {Cacher.CL_NUMBERS: {}, Cacher.TREE: {}, Cacher.TREE_HASH: {}, Cacher.NEXT_BRANCH: "aaaaa"}

    def _init(self):
        self._cache = {Cacher.CL_NUMBERS: {}, Cacher.TREE: {}, Cacher.TREE_HASH: {}, Cacher.NEXT_BRANCH: "aaaaa"}

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