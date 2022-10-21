# Gum
A Mercurial style wrapper for Git.

### Test Structure
Unit tests can be found under the test/ directory. These are split into a test file per source file (under src/) and should call the functions in the source file directly using context.py to gain visibility.

Integration tests are under the testing/ directory. These are split into per-command test files. Each integration test uses the framework in integration.py to create, run commands on and destroy a testing git repository. integration.py also contains various helper functions to make interacting with the test repository easier.

### Linter
Before creating a commit, make sure you run the linter using:
`yapf -i -r --style google .`
For instructions on how to install yapf, [see here](https://github.com/google/yapf#installation).
