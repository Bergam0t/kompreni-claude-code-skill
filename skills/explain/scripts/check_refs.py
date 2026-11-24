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
* Blocks whose info string contains ``illustrative`` are skipped.
* Any other fenced block is reported as unmarked (a warning).
* References written as ``[text](path#L42)``, ``[text](path#L42-L51)`` or
  ``path/file.ext:42`` / ``path/file.ext:42-51`` must point at a file that
  exists and a line range inside it.

Exit status: 0 = no errors (warnings allowed), 1 = errors, 2 = bad usage.
Standard library only; needs git on PATH only for ``@<ref>`` and ``--ref``.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

LOC = re.compile(r"^(?P<path>[^\s:@]+\.\w+):(?P<a>\d+)(?:-(?P<b>\d+))?(?:@(?P<ref>\S+))?$")
LINK = re.compile(r"\]\((?P<path>[^)\s#]+)#L(?P<a>\d+)(?:-L?(?P<b>\d+))?\)")
PLAIN = re.compile(r"(?<![\w/\.@(#-])(?P<path>[\w./\-]+\.[A-Za-z]\w{0,7}):(?P<a>\d+)(?:-(?P<b>\d+))?(?![\w@])")
MDLINK = re.compile(r"\[[^\]]*\]\([^)]*\)")
FENCE = re.compile(r"^(\s*)(`{3,}|~{3,})(.*)$")


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


def norm(lines):
    """Strip trailing space, drop surrounding blank lines, remove common indent."""
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


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default=".", help="repository root (default: current directory)")
    ap.add_argument("--file", help="read the draft from this file instead of stdin")
    ap.add_argument("--ref", help="git ref to read files from instead of the working tree")
    args = ap.parse_args()
    repo = Path(args.repo).resolve()
    if not repo.is_dir():
        print(f"error: {repo} is not a directory", file=sys.stderr)
        return 2
    text = Path(args.file).read_text(encoding="utf-8") if args.file else sys.stdin.read()
    if not text.strip():
        print("error: empty draft", file=sys.stderr)
        return 2

    errors, warnings = [], []
    prose = []
    checked_blocks = 0
    lines = text.splitlines()
    i = 0
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
        tokens = info.replace("{", " ").replace("}", " ").replace(",", " ").split()
        where = f"line {start}"
        if "illustrative" in tokens or (tokens and tokens[0] in ("text", "ascii", "diff-illustrative")):
            continue
        loc = next((LOC.match(t) for t in tokens if LOC.match(t)), None)
        if not loc:
            warnings.append(f"{where}: code block has no location (add `path:LINE-LINE` or mark it `illustrative`)")
            continue
        ref = loc["ref"] or args.ref
        expected = check_range(repo, loc["path"], loc["a"], loc["b"], ref, where, errors)
        if expected is None:
            continue
        checked_blocks += 1
        if norm(body) != norm(expected):
            errors.append(f"{where}: snippet does not match {loc['path']}:{loc['a']}-{loc['b'] or loc['a']}"
                          + (f"@{ref}" if ref else "")
                          + " (copy the lines exactly, or mark the block `illustrative`)")

    seen = set()
    refs = 0
    for n, line in prose:
        found = [(m["path"], m["a"], m["b"]) for m in LINK.finditer(line)]
        found += [(m["path"], m["a"], m["b"]) for m in PLAIN.finditer(MDLINK.sub("", line))]
        for path, a, b in found:
            key = (path, a, b, n)
            if key in seen:
                continue
            seen.add(key)
            refs += 1
            check_range(repo, path, a, b, args.ref, f"line {n}", errors)

    for w in warnings:
        print(f"warning: {w}")
    for e in errors:
        print(f"ERROR: {e}")
    print(f"checked {refs} reference(s) and {checked_blocks} verbatim snippet(s): "
          f"{len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
