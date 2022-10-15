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

import os

current = os.path.dirname(os.path.realpath(__file__))
mainPath = os.path.join(current, "src", "main.py")
home = os.path.expanduser("~")
bashrc = os.path.join(home, ".bashrc")

with open(bashrc, "a") as f:
    f.write(f"\nalias gm='python3 {mainPath}'\n")
os.system(f"source {bashrc}")