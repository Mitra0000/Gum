from abc import ABC, abstractmethod

class UnitTest(ABC):
    methods = []

    @abstractmethod
    def setup(self):
        pass

    @abstractmethod
    def before(self):
        pass

    @abstractmethod
    def after(self):
        pass

    def Test(func):
        UnitTest.methods.append(func)
        return func
    
    def run(self):
        for method in UnitTest.methods:
            self.before()
            method(self)
            self.after()