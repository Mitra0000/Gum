from trie import Trie

class TextDecorators:
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    ENDC = '\033[0m'

import os

class Color:
    Black = "\u001b[30m"
    Red = "\u001b[31m"
    Green = "\u001b[32m"
    Yellow = "\u001b[33m"
    Blue = "\u001b[34m"
    Magenta = "\u001b[35m"
    Cyan = "\u001b[36m"
    White = "\u001b[37m"
    Reset = "\u001b[0m"

def formatText(*args, bold: bool = False, underline: bool = False, color: str = Color.White):
    output = []
    if bold:
        output.append(TextDecorators.BOLD)
    if underline:
        output.append(TextDecorators.UNDERLINE)
    output.append(color)
    message = []
    for arg in args:
        message.append(arg)
    output.append(" ".join(message))
    output.append(f"{TextDecorators.ENDC}{Color.Reset}")
    return "".join(output)

def abbreviateText(text, length = 20):
    return text if len(text) <= length else text[:length - 3] + "..."

def getPrefixesForCommits(commits):
    """ Returns a dictionary populated as follows. { prefix: suffix }"""
    trie = Trie()
    for commit in commits:
        trie.insert(commit)
    return trie.query()

def getUniqueCommitPrefixes(commits):
    trie = Trie()
    for commit in commits:
        trie.insert(commit)
    result = trie.query()
    return {k + v: (k, v) for k, v in result.items()}