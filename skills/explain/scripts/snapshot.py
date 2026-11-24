#!/usr/bin/env python3
"""Record the working tree's state as a git tree, without changing anything.

Prints one line, ``tree=<sha> head=<sha|none>``. Later, ``git diff <old tree>
<new tree>`` shows exactly what changed between two snapshots, including
untracked files and changes made by shell commands or scripts.

How: a temporary copy of the index (outside the repository) takes the current
working tree (``git add -u`` plus untracked, non-ignored files), and
``git write-tree`` stores it. The working tree, the real index, branches,
the stash and HEAD are untouched. The only effect is unreferenced objects in
``.git``, which git cleans up in time.

Untracked files larger than ``--max-untracked-mb`` (default 5) are left out
and listed on stderr, so large data files aren't copied into ``.git``.

Exit status: 0 = printed a snapshot, 2 = not a git repository or git failed.
Standard library only.
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile


def git(repo, *args, env=None, stdin=None):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True,
                          env=env, input=stdin, check=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default=".", help="repository (default: current directory)")
    ap.add_argument("--max-untracked-mb", type=float, default=5.0,
                    help="leave out untracked files larger than this (default 5)")
    args = ap.parse_args()

    try:
        top = git(args.repo, "rev-parse", "--show-toplevel").stdout.decode().strip()
        git_dir = git(args.repo, "rev-parse", "--absolute-git-dir").stdout.decode().strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("error: not a git repository (or git is not installed)", file=sys.stderr)
        return 2
    head = subprocess.run(["git", "-C", top, "rev-parse", "--verify", "-q", "HEAD"],
                          capture_output=True).stdout.decode().strip() or "none"

    tmp_dir = tempfile.mkdtemp(prefix="kompreni-")
    try:
        index = os.path.join(tmp_dir, "index")
        real_index = os.path.join(git_dir, "index")
        if os.path.exists(real_index):
            shutil.copyfile(real_index, index)  # reuses git's file-stat cache: fast
        env = {**os.environ, "GIT_INDEX_FILE": index}

        git(top, "add", "-u", env=env)  # tracked: modified and deleted
        others = git(top, "ls-files", "--others", "--exclude-standard", "-z").stdout
        limit = args.max_untracked_mb * 1024 * 1024
        keep, skipped = [], []
        for raw in filter(None, others.split(b"\0")):
            path = os.path.join(top, os.fsdecode(raw))
            try:
                size = os.path.getsize(path)
            except OSError:
                continue
            (skipped if size > limit else keep).append((raw, size))
        if keep:
            git(top, "add", "--pathspec-from-file=-", "--pathspec-file-nul", env=env,
                stdin=b"\0".join(raw for raw, _ in keep))
        tree = git(top, "write-tree", env=env).stdout.decode().strip()
    except subprocess.CalledProcessError as exc:
        print(f"error: git failed: {exc.stderr.decode(errors='replace').strip()}", file=sys.stderr)
        return 2
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    for raw, size in skipped:
        print(f"skipped untracked file over {args.max_untracked_mb:g} MB: "
              f"{os.fsdecode(raw)} ({size / 1024 / 1024:.1f} MB)", file=sys.stderr)
    print(f"tree={tree} head={head}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
