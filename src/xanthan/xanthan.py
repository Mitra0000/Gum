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

from enum import Enum

from xanthan.cl import CL


class Xanthan:
    """
        This class is an interface to help Gum interact with the underlying code
        review tooling. Subclasses should implement all methods to support a 
        given code review tool (like Github or Gerrit).
    """

    _instance = None

    @classmethod
    def get(cls):
        return cls._instance

    @classmethod
    def set(cls, instance):
        cls._instance = instance

    class UploadResponse(Enum):
        SUCCESS = 0
        UNSPECIFIED_FAILURE = 1

    def __init__(self):
        raise NotImplemented("Xanthan method not implemented.")

    def getCLForBranch(self, branchName: str) -> CL:
        """
            Returns a CL object representing the CL on the branch: branchName.
        """
        raise NotImplemented("Xanthan method not implemented.")

    def uploadChanges(self) -> UploadResponse:
        """
            Uploads the current working commit(s) to the code review tool.
        """
        raise NotImplemented("Xanthan method not implemented.")
