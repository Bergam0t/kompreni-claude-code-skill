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

    # Quarto (.qmd) syntax, used by walkthroughs.

    def run_qmd(self, draft, *extra):
        doc = self.repo / "walkthrough.qmd"
        doc.write_text(draft, encoding="utf-8", newline="\n")
        try:
            p = subprocess.run([sys.executable, str(SCRIPT), "--repo", str(self.repo), "--file", str(doc), *extra],
                               capture_output=True, text=True)
        finally:
            doc.unlink()
        return p.returncode, p.stdout

    def test_qmd_filename_caption_checked(self):
        ok = '```{.python filename="src/a.py:1-2"}\ndef f(x):\n    return x + 2\n```\n'
        code, out = self.run_qmd(ok)
        self.assertEqual(code, 0, out)
        self.assertIn("1 verbatim snippet", out)
        bad = '```{.python filename="src/a.py:1-2"}\ndef f(x):\n    return x + 9\n```\n'
        code, out = self.run_qmd(bad)
        self.assertEqual(code, 1)
        self.assertIn("does not match", out)

    def test_qmd_before_snippet_ref_in_caption(self):
        draft = '```{.python filename="src/a.py:1-2@HEAD"}\ndef f(x):\n    return x + 1\n```\n'
        code, out = self.run_qmd(draft)
        self.assertEqual(code, 0, out)

    def test_qmd_annotation_markers_ignored(self):
        draft = ('```{.python filename="src/a.py:1-2"}\ndef f(x):          # <1>\n    return x + 2    # <2>\n```\n'
                 "1. Entry.\n2. The change.\n")
        code, out = self.run_qmd(draft)
        self.assertEqual(code, 0, out)

    def test_qmd_illustrative_mermaid_and_text_skipped(self):
        draft = ('```{.python .illustrative filename="Simplified from src/a.py"}\nf(1)\n```\n\n'
                 "```{mermaid}\nflowchart LR\n  A --> B\n```\n\n"
                 "```{.text}\nA -> B\n```\n")
        code, out = self.run_qmd(draft)
        self.assertEqual(code, 0, out)
        self.assertIn("0 warning", out)

    def test_qmd_executable_cell_is_error(self):
        code, out = self.run_qmd("```{python}\nprint(1)\n```\n")
        self.assertEqual(code, 1)
        self.assertIn("executable", out)

    def test_qmd_bare_mermaid_warns_but_md_does_not(self):
        draft = "```mermaid\nflowchart LR\n  A --> B\n```\n"
        code, out = self.run_qmd(draft)
        self.assertEqual(code, 0, out)
        self.assertIn("{mermaid}", out)
        code, out = self.run_check(draft)
        self.assertEqual(code, 0, out)
        self.assertIn("0 warning", out)

    def test_qmd_unmarked_braced_block_warns(self):
        code, out = self.run_qmd("```{.python}\nx()\n```\n")
        self.assertEqual(code, 0, out)
        self.assertIn("no location", out)

    def test_front_matter_skipped(self):
        draft = "---\ntitle: \"t\"\nkompreni:\n  files: [src/nope.py:3]\n---\n\nSee `src/a.py:2`.\n"
        code, out = self.run_qmd(draft)
        self.assertEqual(code, 0, out)
        self.assertIn("checked 1 reference", out)

    def test_permalink_checked_at_its_ref(self):
        good = "See [f](https://github.com/o/r/blob/feature/src/a.py#L9-L10).\n"
        code, out = self.run_check(good)
        self.assertEqual(code, 0, out)
        self.assertIn("checked 1 reference", out)
        bad = "See [f](https://github.com/o/r/blob/main/src/a.py#L9-L10).\n"
        self.assertEqual(self.run_check(bad)[0], 1)

    # Code annotations (.qmd).

    ANNOTATED = '```{.python filename="src/a.py:1-2"}\ndef f(x):          # <1>\n    return x + 2    # <2>\n```\n'

    def test_annotations_missing_and_extra_items(self):
        code, out = self.run_qmd(self.ANNOTATED + "1. Entry.\n")
        self.assertEqual(code, 1)
        self.assertIn("marker(s) 2 have no list item", out)
        code, out = self.run_qmd(self.ANNOTATED + "1. Entry.\n2. Change.\n3. Extra.\n")
        self.assertEqual(code, 1)
        self.assertIn("list item(s) 3 have no marker", out)

    def test_annotations_blank_line_ok_prose_between_fails(self):
        code, out = self.run_qmd(self.ANNOTATED + "\n1. Entry.\n2. Change.\n\nAfter the list.\n")
        self.assertEqual(code, 0, out)
        code, out = self.run_qmd(self.ANNOTATED + "Some prose.\n\n1. Entry.\n2. Change.\n")
        self.assertEqual(code, 1)
        self.assertIn("not followed by its numbered list", out)

    def test_annotation_second_paragraph_fails(self):
        code, out = self.run_qmd(self.ANNOTATED + "1. Entry.\n\n    More about the entry.\n2. Change.\n")
        self.assertEqual(code, 1)
        self.assertIn("item 1 has a second paragraph", out)

    def test_annotation_number_shared_by_lines(self):
        draft = '```{.python filename="src/a.py:1-2"}\ndef f(x):          # <1>\n    return x + 2    # <1>\n```\n1. Both.\n'
        code, out = self.run_qmd(draft)
        self.assertEqual(code, 0, out)

    def test_annotation_item_starting_like_a_list_fails(self):
        code, out = self.run_qmd(self.ANNOTATED + "1. - a bullet.\n2. Change.\n")
        self.assertEqual(code, 1)
        self.assertIn("starts like a list", out)

    def test_html_comment_markers_in_markdown_blocks(self):
        (self.repo / "notes.md").write_text("Step one.\nStep two.\n", newline="\n")
        try:
            draft = ('```{.markdown filename="notes.md:1-2"}\nStep one. <!-- <1> -->\nStep two.\n```\n1. First step.\n')
            code, out = self.run_qmd(draft)
            self.assertEqual(code, 0, out)
            code, out = self.run_qmd(draft.replace("1. First step.\n", ""))
            self.assertEqual(code, 1)
            self.assertIn("not followed by its numbered list", out)
        finally:
            (self.repo / "notes.md").unlink()

    def test_annotation_markers_outside_quarto_warn(self):
        code, out = self.run_check("```python src/a.py:1-2\ndef f(x):  # <1>\n    return x + 2\n```\n1. Entry.\n")
        self.assertEqual(code, 0, out)
        self.assertIn("only work in Quarto", out)

    def test_number_lines_start_from(self):
        ok = '```{.python .numberLines startFrom="2" filename="src/a.py:2"}\n    return x + 2\n```\n'
        self.assertEqual(self.run_qmd(ok)[0], 0)
        bad = '```{.python .numberLines filename="src/a.py:2"}\n    return x + 2\n```\n'
        code, out = self.run_qmd(bad)
        self.assertEqual(code, 1)
        self.assertIn('startFrom="2"', out)

    # --coverage

    def test_coverage_reports_unshown_changes(self):
        draft = "```python src/a.py:1-2\ndef f(x):\n    return x + 3\n```\n"
        code, out = self.run_check(draft, "--ref", "feature", "--coverage", "main..feature")
        self.assertEqual(code, 0, out)  # notes never fail the check
        self.assertIn("note: not shown: src/a.py:", out)
        self.assertNotIn("not shown: src/a.py:2\n", out)
        full = "```python src/a.py:1-10\n" + BRANCH + "```\n"
        code, out = self.run_check(full, "--ref", "feature", "--coverage", "main..feature")
        self.assertEqual(code, 0, out)
        self.assertIn("0 changed range(s) not shown", out)

    def test_coverage_ignores_blank_lines(self):
        # Lines 7-8 of the branch's addition are blank; showing 9-10 leaves nothing to report there.
        draft = ("```python src/a.py:1-2\ndef f(x):\n    return x + 3\n```\n\n"
                 "```python src/a.py:9-10\ndef h():\n    pass\n```\n")
        code, out = self.run_check(draft, "--ref", "feature", "--coverage", "main..feature")
        self.assertEqual(code, 0, out)
        self.assertIn("0 changed range(s) not shown", out)

    def test_coverage_against_working_tree(self):
        draft = "```python src/a.py:2\n    return x + 2\n```\n"
        code, out = self.run_check(draft, "--coverage", "HEAD")
        self.assertEqual(code, 0, out)
        self.assertIn("0 changed range(s) not shown", out)

    def test_coverage_deletions_need_a_before_snippet(self):
        after = "```python src/a.py:1-2\ndef f(x):\n    return x + 1\n```\n"
        code, out = self.run_check(after, "--ref", "main", "--coverage", "feature..main")
        self.assertIn("removed lines not shown: src/a.py:", out)
        before = after + "\n```python src/a.py:6-10@feature\n    return y * 2\n\n\ndef h():\n    pass\n```\n"
        code, out = self.run_check(before, "--ref", "main", "--coverage", "feature..main")
        self.assertEqual(code, 0, out)
        self.assertIn("0 changed range(s) not shown", out)

    def test_other_urls_ignored(self):
        code, out = self.run_check("See [docs](https://example.com/guide#L3).\n")
        self.assertEqual(code, 0, out)
        self.assertIn("checked 0 reference", out)


if __name__ == "__main__":
    unittest.main()
