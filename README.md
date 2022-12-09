# Gum
A Mercurial style wrapper for Git.

## Introduction
Gum is a tool designed for use with the Chromium project. Its aim is to simplify the task of creating, modifying and uploading CLs with [Chromium's Gerrit](https://chromium-review.googlesource.com/) tool. A simple example is wanting to make changes to an existing CL checked out on a branch. Once the new changes have been made, a Git user would have to run:
```
$ git cl format
$ git add -A
$ git commit --amend
# Exit the editor which pops up.
$ git cl upload
# Write a patchset title and hit enter.
```
The same in Gum is simplified to:
```
$ gm fix
$ gm amend
$ gm uploadchain
```
Gum also changes how commits and branches work on a fundamental level to make it easier to see how different CLs relate to each other. Support for creating and maintaining chains of dependent CLs is baked into Gum and the `gm xl` command is the best way to see this visually.

### Test Structure
Unit tests can be found under the test/ directory. These are split into a test file per source file (under src/) and should call the functions in the source file directly using context.py to gain visibility.

Integration tests are under the testing/ directory. These are split into per-command test files. Each integration test uses the framework in integration.py to create, run commands on and destroy a testing git repository. integration.py also contains various helper functions to make interacting with the test repository easier.

### Creating PRs
Before creating a commit, make sure you run the linter using:
`yapf -i -r --style google .` from the root directory.
For instructions on how to install yapf, [see here](https://github.com/google/yapf#installation).

It's also best practice to run the unit tests (run `python3 test/test_runner.py`) and the integration tests (run `python3 testing/test_runner.py`) to ensure that the new changes do not cause breakages. If you're adding new functionality, consider writing a unit test or integration test.
