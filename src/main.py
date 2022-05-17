import os
import sys

def main():
    command = sys.argv[1]
    if command == "commit":
        name = sys.argv[2]
        os.system("git commit -m '" + name + "'")
    elif command == "uc":
        os.system("git push")
    else:
        print("Unknown gum command")

if __name__ == '__main__':
    main()
