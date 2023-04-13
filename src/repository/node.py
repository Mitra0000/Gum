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

from dataclasses import dataclass


@dataclass
class Node:
    # The branch name eg. "aaaaa".
    branch: str
    # The full commit hash.
    commit: str
    # The parent commit node.
    parent: "Node"
    # List of child commit nodes.
    children: list["Node"]
    # Boolean denoting whether the change is owned.
    is_owned: bool
    # Shortest unique commit hash prefix.
    commitPrefix: str
    # Remainder of the shortened commit hash.
    commitSuffix: str
