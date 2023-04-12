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


class BoolFeature:

    def __init__(self, enabled: bool):
        self.enabled = enabled

    def __bool__(self):
        return self.enabled

    def __str__(self):
        return str(self.enabled)


class Features:
    # List feature flags here. Should be alphabetical.
    SHOULD_CACHE_TREE = BoolFeature(False)
    SYNC_FOR_UNOWNED_BRANCHES = BoolFeature(False)
    USE_PROTO_FOR_TREE_CACHE = BoolFeature(True)

    @classmethod
    def enableFeaturesForTesting(cls, *features):
        for feature in features:
            feature.enabled = True

    @classmethod
    def disableFeaturesForTesting(cls, *features):
        for feature in features:
            feature.enabled = False
