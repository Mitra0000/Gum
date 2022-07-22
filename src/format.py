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

def format(*args, bold: bool = False, underline: bool = False, color: str = Color.White):
    output = (TextDecorators.BOLD if bold else "") + (TextDecorators.UNDERLINE if underline else "") + color
    for i in args:
        output += i + " "
    output += TextDecorators.ENDC + Color.Reset
    return output