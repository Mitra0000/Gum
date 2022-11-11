class Feature:

    def __init__(self, enabled: bool):
        self.enabled = enabled

    def __bool__(self):
        return self.enabled

    def __str__(self):
        return str(self.enabled)


class Features:
    # List feature flags here.
    SHOULD_CACHE_TREE = Feature(False)
    USE_PROTO_FOR_TREE_CACHE = Feature(True)

    @classmethod
    def enableFeaturesForTesting(cls, *features):
        for feature in features:
            feature.enabled = True

    @classmethod
    def disableFeaturesForTesting(cls, *features):
        for feature in features:
            feature.enabled = False
