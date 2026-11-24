"""Tests for skills/explain/scripts/check_refs.py. Run: python -m unittest discover tests"""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "skills" / "explain" / "scripts" / "check_refs.py"

OLD = "def f(x):\n    return x + 1\n\n\ndef g(y):\n    return y * 2\n"
NEW = "def f(x):\n    return x + 2\n\n\ndef g(y):\n    return y * 2\n"
BRANCH = "def f(x):\n    return x + 3\n\n\ndef g(y):\n    return y * 2\n\n\ndef h():\n    pass\n"


def git(repo, *args):
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


class CheckRefsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo = Path(tempfile.mkdtemp())
        git(cls.repo, "init", "-q", "-b", "main")
        git(cls.repo, "config", "user.email", "t@example.com")
        git(cls.repo, "config", "user.name", "t")
        git(cls.repo, "config", "core.autocrlf", "false")
        (cls.repo / "src").mkdir()
        (cls.repo / "src" / "a.py").write_text(OLD, newline="\n")
        git(cls.repo, "add", ".")
        git(cls.repo, "commit", "-qm", "init")
        # A branch that is not checked out afterwards.
        git(cls.repo, "checkout", "-qb", "feature")
        (cls.repo / "src" / "a.py").write_text(BRANCH, newline="\n")
        git(cls.repo, "commit", "-qam", "feature")
        git(cls.repo, "checkout", "-q", "main")
        # Uncommitted working-tree change on main.
        (cls.repo / "src" / "a.py").write_text(NEW, newline="\n")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.repo, ignore_errors=True)

    def run_check(self, draft, *extra):
        p = subprocess.run([sys.executable, str(SCRIPT), "--repo", str(self.repo), *extra],
                           input=draft, capture_output=True, text=True)
        return p.returncode, p.stdout

    def test_verbatim_match_passes(self):
        code, out = self.run_check("```python src/a.py:1-2\ndef f(x):\n    return x + 2\n```\n")
        self.assertEqual(code, 0, out)

    def test_mismatched_snippet_fails(self):
        code, out = self.run_check("```python src/a.py:5-6\ndef g(y):\n    return y * 3\n```\n")
        self.assertEqual(code, 1)
        self.assertIn("does not match", out)

    def test_missing_file_and_out_of_range(self):
        code, out = self.run_check("See `src/nope.py:3` and `src/a.py:99`.\n")
        self.assertEqual(code, 1)
        self.assertIn("src/nope.py not found", out)
        self.assertIn("outside the file", out)

    def test_before_snippet_at_head(self):
        code, out = self.run_check("```python src/a.py:1-2@HEAD\ndef f(x):\n    return x + 1\n```\n")
        self.assertEqual(code, 0, out)

    def test_link_text_not_treated_as_reference(self):
        code, out = self.run_check("Changed [a.py:2](src/a.py#L2).\n")
        self.assertEqual(code, 0, out)
        self.assertIn("checked 1 reference", out)

    def test_unmarked_block_warns_and_illustrative_skipped(self):
        code, out = self.run_check("```python\nx()\n```\n\n```python illustrative\ny()\n```\n")
        self.assertEqual(code, 0, out)
        self.assertIn("warning: line 1", out)
        self.assertIn("1 warning", out)

    def test_ref_reads_branch_not_checked_out(self):
        draft = ("New `h` at `src/a.py:9-10`.\n\n"
                 "```python src/a.py:1-2\ndef f(x):\n    return x + 3\n```\n")
        self.assertEqual(self.run_check(draft)[0], 1)  # not in the working tree
        code, out = self.run_check(draft, "--ref", "feature")
        self.assertEqual(code, 0, out)

    def test_explicit_ref_overrides_ref_option(self):
        draft = "```python src/a.py:1-2@main\ndef f(x):\n    return x + 1\n```\n"
        code, out = self.run_check(draft, "--ref", "feature")
        self.assertEqual(code, 0, out)


if __name__ == "__main__":
    unittest.main()
