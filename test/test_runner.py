import os
import unittest

def suite():
    loader = unittest.TestLoader()
    return loader.discover(os.path.dirname(os.path.realpath(__file__)), "*_test.py")

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(suite())