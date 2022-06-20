import json
import os

class Cacher:
    CL_NUMBERS = "cl_numbers"
    TREE = "tree"
    PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tmp")
    CL_NUMBERS_JSON = os.path.join(PATH, "clnumbers.json")
    
    @classmethod
    def init(cls):
        if not os.path.exists(cls.PATH):
            os.mkdir(cls.PATH)
            with open(os.path.join(cls.PATH, ".gitignore"), "w") as f:
                f.write("clnumbers.json")
        if not os.path.exists(cls.CL_NUMBERS_JSON):
            with open(cls.CL_NUMBERS_JSON, "w") as f:
                json.dump({}, f)

    @classmethod
    def areClNumbersValid(cls) -> bool:
        return len(self.getCachedClNumbers()) != 0
    
    @classmethod
    def invalidateClNumbers(cls):
        with open(cls.CL_NUMBERS_JSON, "w") as f:
            json.dump({}, f)
    
    @classmethod
    def getCachedClNumbers(cls):
        with open(cls.CL_NUMBERS_JSON, "r") as f:
            numbers = json.load(f)
        return numbers
    
    @classmethod
    def cacheClNumbers(cls, clNumbers):
        with open(cls.CL_NUMBERS_JSON, "w") as f:
            json.dump(clNumbers, f)