# Xanthan

Xanthan is an abstraction layer above the code review tool associated with the Gum repository. This allows Gum to work on Github projects, Gerrit projects, or any other Git based system.

## Adding support

To add support for a system, create a new file subclassing Xanthan in xanthan.py and set the subclass as the Xanthan provider in Gum's config. If the methods are implemented correctly, each provider should just work.