import os
import subprocess

class CommandRunner:
    _instance = None

    @classmethod
    def get(cls):
        if cls._instance is None:
            cls._instance = CommandRunner()
        return cls._instance

    def run(self, command: str) -> str:
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        return out.decode("utf-8")
    
    def runInProcess(self, command: str):
        os.system(command)

    def swapInstanceForTesting(cls, instance):
        cls._instance = instance