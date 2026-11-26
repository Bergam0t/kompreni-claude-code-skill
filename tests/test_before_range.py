"""Tests for skills/explain/scripts/before_range.py. Run: python -m unittest discover tests"""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "skills" / "explain" / "scripts" / "before_range.py"
sys.path.insert(0, str(SCRIPT.parent))
from check_refs import line_kinds, pair_lines  # noqa: E402

# base -> tip: insert after old line 2, replace old line 4, delete old line 6.
BASE = "".join(f"{c} = {n}\n" for n, c in enumerate("abcdefghij", 1))
TIP = "a = 1\nb = 2\nx = 0\nc = 3\nd = 40\ne = 5\ng = 7\nh = 8\ni = 9\nj = 10\n"


def git(repo, *args):
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


class BeforeRangeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo = Path(tempfile.mkdtemp())
        git(cls.repo, "init", "-q", "-b", "main")
        git(cls.repo, "config", "user.email", "t@example.com")
        git(cls.repo, "config", "user.name", "t")
        git(cls.repo, "config", "core.autocrlf", "false")
        (cls.repo / "m.py").write_text(BASE, newline="\n")
        git(cls.repo, "add", ".")
        git(cls.repo, "commit", "-qm", "base")
        git(cls.repo, "tag", "base")
        (cls.repo / "m.py").write_text(TIP, newline="\n")
        (cls.repo / "new.py").write_text("y = 1\n", newline="\n")
        git(cls.repo, "add", ".")
        git(cls.repo, "commit", "-qm", "tip")
        git(cls.repo, "tag", "tip")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.repo, ignore_errors=True)

    def run_it(self, *args, spec="base..tip"):
        p = subprocess.run([sys.executable, str(SCRIPT), "--repo", str(self.repo), spec, *args],
                           capture_output=True, text=True)
        return p.returncode, p.stdout + p.stderr

    def test_replaced_line(self):
        code, out = self.run_it("m.py:5")
        self.assertEqual(code, 0, out)
        self.assertIn('After:  .numberLines startFrom="5" changed="5" filename="m.py:5"', out)
        self.assertIn('Before: .numberLines startFrom="4" changed="4" filename="m.py:4@base"', out)

    def test_unchanged_lines_shift_by_earlier_hunks(self):
        code, out = self.run_it("m.py:7-8")
        self.assertEqual(code, 0, out)
        self.assertIn('Before: .numberLines startFrom="7" filename="m.py:7-8@base"', out)
        code, out = self.run_it("m.py:4")
        self.assertIn('filename="m.py:3@base"', out)

    def test_range_spanning_a_deletion_includes_it(self):
        code, out = self.run_it("m.py:6-7")
        self.assertEqual(code, 0, out)
        self.assertIn('After:  .numberLines startFrom="6" filename="m.py:6-7"', out)
        self.assertIn('Before: .numberLines startFrom="5" removed="6" filename="m.py:5-7@base"', out)

    def test_pure_addition_suggests_surrounding_lines(self):
        code, out = self.run_it("m.py:3")
        self.assertEqual(code, 0, out)
        self.assertIn('After:  .numberLines startFrom="3" added="3" filename="m.py:3"', out)
        self.assertIn('Before: .numberLines startFrom="1" filename="m.py:1-3@base"', out)
        self.assertIn("pure addition after old line 2", out)

    def test_old_override_gives_marks_for_widened_ranges(self):
        code, out = self.run_it("m.py:1-6", "--old", "1-5")
        self.assertEqual(code, 0, out)
        self.assertIn('After:  .numberLines startFrom="1" changed="5" added="3" filename="m.py:1-6"', out)
        self.assertIn('Before: .numberLines startFrom="1" changed="4" filename="m.py:1-5@base"', out)

    def test_new_file_has_no_before(self):
        code, out = self.run_it("new.py:1")
        self.assertEqual(code, 1)
        self.assertIn("no Before", out)

    def test_out_of_range(self):
        code, out = self.run_it("m.py:9-12")
        self.assertEqual(code, 1)
        self.assertIn("outside the file", out)

    def test_working_tree_tip(self):
        (self.repo / "m.py").write_text(TIP.replace("j = 10", "j = 11"), newline="\n")
        try:
            code, out = self.run_it("m.py:10", spec="tip")
            self.assertEqual(code, 0, out)
            self.assertIn('Before: .numberLines startFrom="10" changed="10" filename="m.py:10@tip"', out)
        finally:
            git(self.repo, "checkout", "--", "m.py")


class LineKindsTest(unittest.TestCase):
    def test_uneven_hunk_pairs_similar_lines_in_order(self):
        old = ["total = 0", "for x in xs:", "    total += x"]
        new = ["total = 0.0", "# sum the values", "for x in xs:", "    total += float(x)", "return total"]
        # One hunk: old lines 1-3 replaced by new lines 1-5.
        old_k, new_k = line_kinds([(1, 3, 1, 5)], old, new)
        self.assertEqual(old_k, {1: "changed", 2: "changed", 3: "changed"})
        self.assertEqual(new_k, {1: "changed", 2: "added", 3: "changed", 4: "changed", 5: "added"})

    def test_dissimilar_lines_are_removed_and_added(self):
        old_k, new_k = line_kinds([(1, 1, 1, 1)], ["import os"], ["class Store:"])
        self.assertEqual((old_k, new_k), ({1: "removed"}, {1: "added"}))

    def test_blank_lines_never_pair(self):
        self.assertEqual(pair_lines(["", "a = 1"], ["", "a = 2"]), [(1, 1)])


if __name__ == "__main__":
    unittest.main()
