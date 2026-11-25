#!/usr/bin/env python3
"""Check the code references and snippets in a draft Kompreni explanation.

Reads the draft from stdin (or --file) and checks it against the repository:

* Fenced code blocks whose info string has a location token
  (``path/to/file.py:10-14`` or ``path/to/file.py:10-14@<git-ref>``) must
  match those lines exactly (ignoring indentation and trailing spaces).
  ``@<ref>`` reads the file as it was at that ref, for "before" snippets.
* ``--ref <git-ref>`` reads every reference and snippet without its own
  ``@<ref>`` from that ref instead of the working tree (for explaining a
  branch or commit that isn't checked out).
* Blocks whose info string contains ``illustrative`` are skipped, as are
  ``text`` sketches and mermaid diagrams.
* Any other fenced block is reported as unmarked (a warning).
* Quarto blocks use the braced form: ``{.python filename="src/a.py:10-14"}``
  is checked like a location token, ``{.python .illustrative ...}`` and
  ``{mermaid}`` are skipped, and an executable cell such as ``{python}`` is
  an error. Code-annotation markers (``# <1>``) are ignored when comparing.
* References written as ``[text](path#L42)``, ``[text](path#L42-L51)`` or
  ``path/file.ext:42`` / ``path/file.ext:42-51`` must point at a file that
  exists and a line range inside it. GitHub permalinks
  (``https://github.com/o/r/blob/<ref>/path#L42``) are checked at ``<ref>``;
  other URLs are ignored.
* A YAML front matter block at the top of the draft is skipped.
* Quarto code annotations (.qmd only): every ``# <n>`` marker in a block needs
  item ``n`` in the numbered list straight after it, every item needs a
  marker, and an item can't have a second paragraph (Quarto drops it). These
  are errors, because Quarto mostly fails silently. Outside .qmd, markers
  are a warning. ``.numberLines`` needs ``startFrom`` equal to the first line.
* ``--coverage BASE[..TIP]`` lists the changed lines that no verbatim snippet
  shows (new-side lines against snippets at the tip; deletion-only hunks
  against ``@<ref>`` snippets), as notes that don't change the exit status.

Exit status: 0 = no errors (warnings allowed), 1 = errors, 2 = bad usage.
Standard library only; needs git on PATH only for ``@<ref>``, ``--ref`` and
permalinks.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

LOC = re.compile(r"^(?P<path>[^\s:@]+\.\w+):(?P<a>\d+)(?:-(?P<b>\d+))?(?:@(?P<ref>\S+))?$")
LINK = re.compile(r"\]\((?P<path>[^)\s#]+)#L(?P<a>\d+)(?:-L?(?P<b>\d+))?\)")
PERMALINK = re.compile(r"^https?://[^/]+/[^/]+/[^/]+/blob/(?P<ref>[^/]+)/(?P<path>.+)$")
PLAIN = re.compile(r"(?<![\w/\.@(#-])(?P<path>[\w./\-]+\.[A-Za-z]\w{0,7}):(?P<a>\d+)(?:-(?P<b>\d+))?(?![\w@])")
MDLINK = re.compile(r"\[[^\]]*\]\([^)]*\)")
FENCE = re.compile(r"^(\s*)(`{3,}|~{3,})(.*)$")
ATTR = re.compile(r'([\w-]+)\s*=\s*(?:"([^"]*)"|([^\s"}]+))')
# Quarto annotation markers: a line comment (# // -- ;) or a block comment (<!-- --> or /* */) holding <n>.
_MARK = r"(?:(?:#|//|--|;)\s*<(\d+)>|<!--\s*<(\d+)>\s*-->|/\*\s*<(\d+)>\s*\*/)\s*$"
ANNOTATION = re.compile(r"\s*" + _MARK)
MARKER = re.compile(_MARK)
LIST_ITEM = re.compile(r"^(\d+)\.\s+(.*)$")
# Item text that Pandoc reads as a nested block (list, heading, quote): Quarto's annotation filter crashes on it.
BLOCK_START = re.compile(r"^([-*+](\s|$)|\d+[.)](\s|$)|[A-Za-z][.)](\s|$)|#{1,6}\s|>)")
HUNK = re.compile(r"^@@ -(?P<oa>\d+)(?:,(?P<ob>\d+))? \+(?P<na>\d+)(?:,(?P<nb>\d+))? @@")
SKETCH_LANGS = ("text", "ascii", "diff-illustrative")


def read_lines(repo, path, ref):
    """Return the file's lines, or None if it can't be read."""
    path = path.replace("\\", "/")
    if ref:
        try:
            out = subprocess.run(["git", "-C", str(repo), "show", f"{ref}:{path}"],
                                 capture_output=True, text=True, check=True).stdout
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None
        return out.splitlines()
    f = (repo / path)
    if not f.is_file():
        return None
    return f.read_text(encoding="utf-8", errors="replace").splitlines()


def norm(lines, strip_annotations=False):
    """Strip trailing space, drop surrounding blank lines, remove common indent."""
    if strip_annotations:
        lines = [ANNOTATION.sub("", l) for l in lines]
    lines = [l.rstrip() for l in lines]
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    indents = [len(l) - len(l.lstrip()) for l in lines if l]
    cut = min(indents) if indents else 0
    return [l[cut:] for l in lines]


def check_range(repo, path, a, b, ref, where, errors):
    lines = read_lines(repo, path, ref)
    where_ref = f" at {ref}" if ref else ""
    if lines is None:
        errors.append(f"{where}: {path}{where_ref} not found")
        return None
    a, b = int(a), int(b or a)
    if a < 1 or b < a or b > len(lines):
        errors.append(f"{where}: {path}:{a}-{b}{where_ref} is outside the file ({len(lines)} lines)")
        return None
    return lines[a - 1:b]


def classify(info):
    """Return (kind, location match or None) for a fence's info string.

    kind is one of: "verbatim", "skip", "mermaid", "executable", "unmarked".
    """
    if info.startswith("{"):
        inner = info.strip().strip("{}").strip()
        attrs = {m.group(1): m.group(2) if m.group(2) is not None else m.group(3) for m in ATTR.finditer(inner)}
        tokens = ATTR.sub(" ", inner).split()
        first = tokens[0] if tokens else ""
        if first in ("mermaid", ".mermaid"):
            return "mermaid", None
        if first and not first.startswith("."):
            return "executable", None
        classes = [t[1:] for t in tokens if t.startswith(".")]
        if "illustrative" in classes:
            return "skip", None
        loc = LOC.match(attrs.get("filename", "").strip())
        if loc:
            return "verbatim", loc
        if classes and classes[0] in SKETCH_LANGS:
            return "skip", None
        return "unmarked", None
    tokens = info.replace(",", " ").split()
    if "illustrative" in tokens or (tokens and tokens[0] in SKETCH_LANGS):
        return "skip", None
    if tokens and tokens[0] == "mermaid":
        return "mermaid", None
    loc = next((LOC.match(t) for t in tokens if LOC.match(t)), None)
    return ("verbatim", loc) if loc else ("unmarked", None)


def braced_attrs(info):
    """key=value attributes of a braced (Quarto) info string; {} otherwise."""
    if not info.startswith("{"):
        return {}
    return {m.group(1): m.group(2) if m.group(2) is not None else m.group(3) for m in ATTR.finditer(info)}


def check_annotations(body, lines, after, where, is_qmd, errors, warnings):
    """Quarto code annotations: every `# <n>` marker needs list item n, in an ordered list that
    follows the block (blank lines allowed, nothing else). Quarto silently drops the links when
    prose comes between, ignores markers with no item, and drops an item's second paragraph."""
    markers = {int(next(g for g in m.groups() if g)) for line in body for m in [MARKER.search(line)] if m}
    if not markers:
        return
    if not is_qmd:
        warnings.append(f"{where}: annotation markers (`# <n>`) only work in Quarto; outside it they show as text")
        return
    j = after
    while j < len(lines) and not lines[j].strip():
        j += 1
    if j >= len(lines) or not LIST_ITEM.match(lines[j]):
        errors.append(f"{where}: annotated block is not followed by its numbered list "
                      "(Quarto drops the annotations if anything but blank lines comes between)")
        return
    items, blank = [], False
    while j < len(lines):
        line = lines[j]
        item = LIST_ITEM.match(line)
        if item:
            items.append(int(item.group(1)))
            if BLOCK_START.match(item.group(2)):
                errors.append(f"line {j + 1}: annotation item {item.group(1)} starts like a list, heading or quote "
                              f"({item.group(2)[:12]!r}); Quarto's render fails on it. Start with a word")
            blank = False
        elif not line.strip():
            blank = True
        elif blank and line[:1] in (" ", "\t"):
            errors.append(f"line {j + 1}: annotation item {items[-1]} has a second paragraph; "
                          "Quarto drops it. Keep each item to one paragraph")
            blank = False
        elif blank:
            break  # the list has ended
        j += 1
    missing = sorted(markers - set(items))
    extra = sorted(set(items) - markers)
    if missing:
        errors.append(f"{where}: annotation marker(s) {', '.join(map(str, missing))} have no list item")
    if extra:
        errors.append(f"{where}: list item(s) {', '.join(map(str, extra))} have no marker in the block")


def changed_ranges(repo, spec):
    """Hunks of `git diff -U0 <base> [<tip>]` for spec 'base' or 'base..tip'.

    Returns (added, removed): added maps path -> list of (a, b) new-side line ranges;
    removed maps path -> list of (a, b, after) old-side ranges of deletion-only hunks.
    """
    base, _, tip = spec.partition("..")
    cmd = ["git", "-C", str(repo), "diff", "-U0", "--no-color", "--no-ext-diff", base] + ([tip] if tip else []) + ["--"]
    out = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True).stdout
    added, removed = {}, {}
    old_path = new_path = None
    for line in out.splitlines():
        if line.startswith("--- "):
            old_path = None if line[4:] == "/dev/null" else line[4:].removeprefix("a/")
        elif line.startswith("+++ "):
            new_path = None if line[4:] == "/dev/null" else line[4:].removeprefix("b/")
        elif line.startswith("@@"):
            h = HUNK.match(line)
            if not h:
                continue
            oa, ob = int(h["oa"]), int(h["ob"] or 1)
            na, nb = int(h["na"]), int(h["nb"] or 1)
            if nb > 0 and new_path:
                added.setdefault(new_path, []).append((na, na + nb - 1))
            elif ob > 0 and (old_path or new_path):
                removed.setdefault(old_path or new_path, []).append((oa, oa + ob - 1, na))
    return added, removed


def uncovered(a, b, shown):
    """Sub-ranges of a..b not inside any of the shown (a, b) ranges."""
    gaps, start = [], None
    for n in range(a, b + 1):
        hit = any(sa <= n <= sb for sa, sb in shown)
        if not hit and start is None:
            start = n
        if hit and start is not None:
            gaps.append((start, n - 1))
            start = None
    if start is not None:
        gaps.append((start, b))
    return gaps


def runs(numbers):
    """Consecutive runs in a sorted list of line numbers, as (a, b) pairs."""
    out = []
    for n in numbers:
        if out and n == out[-1][1] + 1:
            out[-1] = (out[-1][0], n)
        else:
            out.append((n, n))
    return out


def fmt_range(a, b):
    return f"{a}" if a == b else f"{a}-{b}"


def front_matter_end(lines):
    """Index of the first line after a leading YAML front matter block (0 if none)."""
    if not lines or lines[0].strip() != "---":
        return 0
    for i in range(1, len(lines)):
        if lines[i].strip() in ("---", "..."):
            return i + 1
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default=".", help="repository root (default: current directory)")
    ap.add_argument("--file", help="read the draft from this file instead of stdin")
    ap.add_argument("--ref", help="git ref to read files from instead of the working tree")
    ap.add_argument("--coverage", metavar="BASE[..TIP]",
                    help="also list changed lines (git diff BASE TIP, or BASE against the working tree) "
                         "that no verbatim snippet shows. Reported as notes, not errors")
    args = ap.parse_args()
    repo = Path(args.repo).resolve()
    if not repo.is_dir():
        print(f"error: {repo} is not a directory", file=sys.stderr)
        return 2
    text = Path(args.file).read_text(encoding="utf-8") if args.file else sys.stdin.read()
    if not text.strip():
        print("error: empty draft", file=sys.stderr)
        return 2

    is_qmd = bool(args.file) and args.file.lower().endswith(".qmd")
    errors, warnings = [], []
    prose = []
    checked_blocks = 0
    shown_new, shown_old = {}, {}  # path -> [(a, b)] shown at the tip / at an explicit @ref
    lines = text.splitlines()
    i = front_matter_end(lines)
    while i < len(lines):
        m = FENCE.match(lines[i])
        if not m:
            prose.append((i + 1, lines[i]))
            i += 1
            continue
        start, fence, info = i + 1, m.group(2), m.group(3).strip()
        body = []
        i += 1
        while i < len(lines):
            close = FENCE.match(lines[i])
            if close and close.group(2)[0] == fence[0] and len(close.group(2)) >= len(fence) and not close.group(3).strip():
                break
            body.append(lines[i])
            i += 1
        i += 1
        where = f"line {start}"
        kind, loc = classify(info)
        if kind != "mermaid":
            check_annotations(body, lines, i, where, is_qmd, errors, warnings)
        if kind == "skip":
            continue
        if kind == "mermaid":
            if is_qmd and not info.startswith("{"):
                warnings.append(f"{where}: Quarto doesn't render ```mermaid; use ```{{mermaid}}")
            continue
        if kind == "executable":
            errors.append(f"{where}: `{info}` is an executable Quarto cell; use the braced class form "
                          f"(e.g. `{{.python filename=\"path:LINE-LINE\"}}`)")
            continue
        if kind == "unmarked":
            warnings.append(f"{where}: code block has no location (add `path:LINE-LINE` or mark it `illustrative`)")
            continue
        attrs = braced_attrs(info)
        if ".numberLines" in info and attrs.get("startFrom", "1") != loc["a"]:
            errors.append(f"{where}: .numberLines needs startFrom=\"{loc['a']}\" so the numbers match the file")
        ref = loc["ref"] or args.ref
        expected = check_range(repo, loc["path"], loc["a"], loc["b"], ref, where, errors)
        if expected is None:
            continue
        checked_blocks += 1
        a, b = int(loc["a"]), int(loc["b"] or loc["a"])
        (shown_old if loc["ref"] else shown_new).setdefault(loc["path"], []).append((a, b))
        if norm(body, strip_annotations=True) != norm(expected):
            errors.append(f"{where}: snippet does not match {loc['path']}:{loc['a']}-{loc['b'] or loc['a']}"
                          + (f"@{ref}" if ref else "")
                          + " (copy the lines exactly, or mark the block `illustrative`)")

    seen = set()
    refs = 0
    for n, line in prose:
        found = []
        for m in LINK.finditer(line):
            path, ref = m["path"], args.ref
            if "://" in path:
                perma = PERMALINK.match(path)
                if not perma:
                    continue  # another URL: not ours to check
                path, ref = perma["path"], perma["ref"]
            found.append((path, m["a"], m["b"], ref))
        found += [(m["path"], m["a"], m["b"], args.ref) for m in PLAIN.finditer(MDLINK.sub("", line))]
        for path, a, b, ref in found:
            key = (path, a, b, ref, n)
            if key in seen:
                continue
            seen.add(key)
            refs += 1
            check_range(repo, path, a, b, ref, f"line {n}", errors)

    notes = []
    if args.coverage:
        try:
            added, removed = changed_ranges(repo, args.coverage)
        except (subprocess.CalledProcessError, FileNotFoundError) as exc:
            print(f"error: --coverage: git diff failed: {getattr(exc, 'stderr', '') or exc}", file=sys.stderr)
            return 2
        tip = args.coverage.partition("..")[2] or args.ref
        for path in sorted(added):
            content = read_lines(repo, path, tip) or []
            # Blank lines never need showing: drop them from each changed range before looking for gaps.
            filled = lambda n: n > len(content) or content[n - 1].strip() != ""
            for a, b in added[path]:
                for ga, gb in uncovered(a, b, shown_new.get(path, [])):
                    keep = [n for n in range(ga, gb + 1) if filled(n)]
                    for run in runs(keep):
                        notes.append(f"not shown: {path}:{fmt_range(*run)}")
        for path in sorted(removed):
            for a, b, after in removed[path]:
                if uncovered(a, b, shown_old.get(path, [])):
                    notes.append(f"removed lines not shown: {path}:{fmt_range(a, b)} (old numbering), "
                                 f"after new line {after}")

    for w in warnings:
        print(f"warning: {w}")
    for e in errors:
        print(f"ERROR: {e}")
    for n in notes:
        print(f"note: {n}")
    print(f"checked {refs} reference(s) and {checked_blocks} verbatim snippet(s): "
          f"{len(errors)} error(s), {len(warnings)} warning(s)"
          + (f", {len(notes)} changed range(s) not shown" if args.coverage else ""))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
