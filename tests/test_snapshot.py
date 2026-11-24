"""Tests for skills/explain/scripts/snapshot.py. Run: python -m unittest discover tests"""
import hashlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "skills" / "explain" / "scripts" / "snapshot.py"


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True,
                          capture_output=True, text=True).stdout


def snapshot(repo, *extra):
    p = subprocess.run([sys.executable, str(SCRIPT), "--repo", str(repo), *extra],
                       capture_output=True, text=True)
    return p.returncode, p.stdout.strip(), p.stderr


def parse(line):
    return dict(part.split("=") for part in line.split())


class SnapshotTest(unittest.TestCase):
    def setUp(self):
        self.repo = Path(tempfile.mkdtemp())
        git(self.repo, "init", "-q", "-b", "main")
        git(self.repo, "config", "user.email", "t@example.com")
        git(self.repo, "config", "user.name", "t")
        (self.repo / "a.py").write_text("one\n")
        (self.repo / ".gitignore").write_text("ignored.txt\n")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-qm", "init")

    def tearDown(self):
        shutil.rmtree(self.repo, ignore_errors=True)

    def test_diff_between_snapshots_includes_untracked_and_deletions(self):
        code, first, _ = snapshot(self.repo)
        self.assertEqual(code, 0)
        (self.repo / "a.py").write_text("two\n")
        (self.repo / "new.py").write_text("x\n")
        (self.repo / "ignored.txt").write_text("secret\n")
        (self.repo / ".gitignore").unlink()
        _, second, _ = snapshot(self.repo)
        changed = git(self.repo, "diff", "--name-status", parse(first)["tree"], parse(second)["tree"])
        self.assertIn("M\ta.py", changed)
        self.assertIn("A\tnew.py", changed)
        self.assertIn("D\t.gitignore", changed)

    def test_ignored_files_left_out(self):
        (self.repo / "ignored.txt").write_text("secret\n")
        _, line, _ = snapshot(self.repo)
        files = git(self.repo, "ls-tree", "-r", "--name-only", parse(line)["tree"])
        self.assertNotIn("ignored.txt", files)

    def test_changes_nothing(self):
        (self.repo / "a.py").write_text("staged\n")
        git(self.repo, "add", "a.py")
        (self.repo / "a.py").write_text("unstaged\n")
        (self.repo / "new.py").write_text("x\n")
        index = self.repo / ".git" / "index"
        before = (git(self.repo, "status", "--porcelain"), hashlib.sha1(index.read_bytes()).hexdigest(),
                  git(self.repo, "rev-parse", "HEAD"), git(self.repo, "stash", "list"))
        snapshot(self.repo)
        after = (git(self.repo, "status", "--porcelain"), hashlib.sha1(index.read_bytes()).hexdigest(),
                 git(self.repo, "rev-parse", "HEAD"), git(self.repo, "stash", "list"))
        self.assertEqual(before, after)
        self.assertEqual((self.repo / "a.py").read_text(), "unstaged\n")

    def test_records_head_and_sees_commits(self):
        _, first, _ = snapshot(self.repo)
        (self.repo / "a.py").write_text("committed\n")
        git(self.repo, "commit", "-qam", "change")
        _, second, _ = snapshot(self.repo)
        self.assertNotEqual(parse(first)["head"], parse(second)["head"])
        changed = git(self.repo, "diff", "--name-only", parse(first)["tree"], parse(second)["tree"])
        self.assertIn("a.py", changed)

    def test_large_untracked_file_skipped(self):
        (self.repo / "big.csv").write_bytes(b"x" * 20000)
        code, line, err = snapshot(self.repo, "--max-untracked-mb", "0.01")
        self.assertEqual(code, 0)
        self.assertIn("skipped untracked file", err)
        self.assertIn("big.csv", err)
        files = git(self.repo, "ls-tree", "-r", "--name-only", parse(line)["tree"])
        self.assertNotIn("big.csv", files)

    def test_repo_without_commits(self):
        fresh = Path(tempfile.mkdtemp())
        try:
            git(fresh, "init", "-q")
            (fresh / "f.txt").write_text("x\n")
            code, line, _ = snapshot(fresh)
            self.assertEqual(code, 0)
            self.assertEqual(parse(line)["head"], "none")
        finally:
            shutil.rmtree(fresh, ignore_errors=True)

    def test_not_a_repo(self):
        plain = Path(tempfile.mkdtemp())
        try:
            code, _, err = snapshot(plain)
            self.assertEqual(code, 2)
            self.assertIn("not a git repository", err)
        finally:
            shutil.rmtree(plain, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
