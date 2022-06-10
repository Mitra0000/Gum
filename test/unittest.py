from abc import ABC, abstractmethod

class UnitTest(ABC):
    methods = []

    def setup(self):
        """ Method called before all tests. """
        pass

    def before(self):
        """ Method called before each test. """
        pass

    def after(self):
        """ Method called after each test. """
        pass

    def Test(func):
        UnitTest.methods.append(func)
        return func
    
    def run(self):
        for method in UnitTest.methods:
            self.before()
            method(self)
            self.after()
        UnitTest.methods = []
    
def assertEquals(actual, expected):
    assert actual == expected, f"Expected: {expected} but was actually {actual}."