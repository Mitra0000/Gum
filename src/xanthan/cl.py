# Copyright 2023 The Gum Authors
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
from enum import Enum

class Status(Enum):
    # The CL has not been sent for review yet.
    DRAFT = 0
    # The CL is currently under review.
    IN_REVIEW = 1
    # The CL has been successfully merged into the repository.
    MERGED = 2
    # The CL is no longer active and the changes have been abandoned.
    ABANDONED = 3

@dataclass(frozen = True)
class CL:
    url: str
    status: Status