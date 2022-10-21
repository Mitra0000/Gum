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

import argparse


def getArgs():
    parser = argparse.ArgumentParser(
        prog="gm", description="Gum: A Mercurial Style Git Wrapper.")
    subparsers = parser.add_subparsers(dest="command")

    add_parser = subparsers.add_parser("add",
                                       help="Add untracked files to Gum.")
    add_parser.add_argument("files", action="append", nargs="*", type=str)

    amend_parser = subparsers.add_parser(
        "amend", help="Update the current commit with the latest changes.")

    commit_parser = subparsers.add_parser(
        "commit", help="Create a new commit as a child of the current commit.")
    commit_parser.add_argument("-m",
                               "--message",
                               help="Add a message for the commit.",
                               required=False)

    continue_parser = subparsers.add_parser(
        "continue", help="Continues an in-progress rebase.")
    diff_parser = subparsers.add_parser(
        "diff", help="Show changes made since the last commit/amendment.")
    fix_parser = subparsers.add_parser(
        "fix", help="Run a linter to automatically format code.")

    forget_parser = subparsers.add_parser("forget",
                                          help="Stop tracking a file or path.")
    forget_parser.add_argument("files", action="append", nargs="*", type=str)

    init_parser = subparsers.add_parser(
        "init",
        help=
        "Initialise a repository to be Gum compatible. This will delete any existing changes."
    )

    patch_parser = subparsers.add_parser(
        "patch",
        help="Locally checkout an existing Chromium CL to modify or extend.")
    patch_parser.add_argument("cl", help="The Gerrit URL of the CL to patch.")
    patch_parser.add_argument(
        "--copy",
        help=
        "Create a copy of the CL so that uploads don't overwrite the existing CL.",
        action="store_true")

    prune_parser = subparsers.add_parser(
        "prune", help="Remove a commit from the local repository.")
    prune_parser.add_argument("commit",
                              help="The commit hash of the commit to remove.")

    rebase_parser = subparsers.add_parser(
        "rebase", help="Move a commit onto another commit.")
    rebase_parser.add_argument("-s",
                               "--source",
                               help="The commit to be moved.",
                               required=True)
    rebase_parser.add_argument(
        "-d",
        "--destination",
        help=
        "The commit that the commit being rebased should be moved on top of.",
        required=True)

    revert_parser = subparsers.add_parser(
        "revert", help="Undo any changes made to a specific file/pathspec.")
    revert_parser.add_argument("files", action="append", nargs="*", type=str)

    status_parser = subparsers.add_parser(
        "status",
        help=
        "Get a list of added, modified, deleted and untracked files since the last commit/amendment."
    )
    sync_parser = subparsers.add_parser(
        "sync", help="Sync the current commit to the newest point upstream.")
    test_parser = subparsers.add_parser(
        "test", help="DO NOT USE. Undefined behaviour meant for testing.")
    uncommit_parser = subparsers.add_parser(
        "uncommit",
        help=
        "Undo the last commit and move the changes into the local repository.")

    update_parser = subparsers.add_parser(
        "update", help="Checkout a different commit to make changes.")
    update_parser.add_argument(
        "commit", help="The commit hash of the commit to update to.")

    uploadchain_parser = subparsers.add_parser(
        "uploadchain",
        aliases=["uc"],
        help=
        "Upload the currently checked out commit along with any direct ancestors."
    )
    uploadtree_parser = subparsers.add_parser(
        "uploadtree",
        aliases=["ut"],
        help="Upload the currently checked out commit along with any children.")
    xl_parser = subparsers.add_parser("xl",
                                      help="Display the current commit tree.")

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Display all Git commands which are run under the hood.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Display the Git commands but don't actually run them.")

    args = parser.parse_known_args()
    args = parser.parse_args(args[1], args[0])
    return args
