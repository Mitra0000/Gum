import glob
import os

from main_test import CommandParserTest

def main():
    test = CommandParserTest()
    test.setup()
    test.run()

if __name__ == '__main__':
    main()