import os
import sys
import subprocess

from format import *

def runCommand(command: str) -> str:
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    return str(out)

def main():
    command = sys.argv[1]
    if command == "commit":
        name = sys.argv[2]
        os.system("git commit -m '" + name + "'")
    elif command == "uc":
        os.system("git push")
    elif command == "status":
       out = runCommand("git status")
       index = out.find("working directory)") + 24
       out = out[index:]
       index = out.find("\\n\\n")
       out = out[:index]
       print(format(out, bold=True, color=Color.Green))
    else:
        print("Unknown gum command")

if __name__ == '__main__':
    main()
