# Copyright 2022 The Gum Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re

from trie import Trie


class TextDecorators:
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    ENDC = '\033[0m'


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


def formatText(*args,
               bold: bool = False,
               underline: bool = False,
               color: str = Color.White):
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


def decodeFormattedText(text: str) -> str:
    return re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])').sub('', text)


def abbreviateText(text, length=20):
    return text if len(text) <= length else text[:length - 3] + "..."


def getUniqueCommitPrefixes(commits):
    trie = Trie()
    for commit in commits:
        trie.insert(commit)
    result = trie.query()
    return {k + v: (k, v) for k, v in result.items()}
