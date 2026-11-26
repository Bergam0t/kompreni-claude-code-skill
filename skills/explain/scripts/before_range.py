#!/usr/bin/env python3
"""Find the old code that matches a block of new code, for a Before/After tabset.

    python before_range.py --repo . BASE[..TIP] path/to/file.py:A-B [--old OA-OB] [--context N]

Maps new lines A-B (at TIP, or in the working tree if there is no TIP) to the lines
they replace at BASE, through the hunks of ``git diff -U0``:

* an unchanged line maps to its old line, shifted by the hunks before it;
* a line inside a hunk maps to the whole of that hunk's old lines;
* lines deleted between A and B are included;
* if nothing maps (a pure addition), it reports where the lines were inserted and
  suggests the old lines either side of that point.

It prints the attributes for both blocks: ``startFrom``, the line marks and
``filename``. The marks are in the file's own numbering: ``changed`` (a line with
a similar counterpart on the other side), ``added`` (After only) and ``removed``
(Before only); see ``check_refs.line_kinds``. It also prints the old lines with
numbers and some context, so the agent can widen both blocks to the same whole
unit. After widening, run it again with the widened new range and
``--old OA-OB`` to get the marks for the final ranges.

Exit status: 0 = printed, 1 = no Before (new file) or bad range, 2 = bad usage or git failure.
Standard library only; needs git on PATH.
"""
import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_refs import (LOC, clean_path, diff_files, fmt_kinds, fmt_range, line_kinds,  # noqa: E402
                        read_lines)


def ends(hunk):
    """Exclusive old and new end positions of a hunk (where unchanged lines resume)."""
    oa, ob, na, nb = hunk
    return (oa + ob if ob else oa + 1), (na + nb if nb else na + 1)


def map_to_old(hunks, a, b):
    """Old line numbers matching new lines a..b, and the old line a pure addition follows."""
    old, insert_after = set(), None
    for n in range(a, b + 1):
        inside = next((h for h in hunks if h[3] and h[2] <= n < h[2] + h[3]), None)
        if inside:
            oa, ob, _, _ = inside
            old.update(range(oa, oa + ob))
            if not ob and insert_after is None:
                insert_after = oa
            continue
        offset = 0
        for h in hunks:
            old_end, new_end = ends(h)
            if new_end <= n:
                offset = old_end - new_end
        old.add(n + offset)
    for oa, ob, na, nb in hunks:
        if not nb and a <= na < b:  # deleted between new lines na and na + 1
            old.update(range(oa, oa + ob))
    return old, insert_after


def parse_range(text):
    a, _, b = text.partition("-")
    a, b = int(a), int(b or a)
    if a < 1 or b < a:
        raise ValueError(text)
    return a, b


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default=".", help="repository root (default: current directory)")
    ap.add_argument("spec", metavar="BASE[..TIP]", help="the change: BASE..TIP, or BASE against the working tree")
    ap.add_argument("location", metavar="PATH:A-B", help="the After block's lines, at TIP")
    ap.add_argument("--old", metavar="OA-OB", help="use these old lines for the Before block (after widening)")
    ap.add_argument("--context", type=int, default=3, help="old lines of context to show either side (default 3)")
    args = ap.parse_args()
    repo = Path(args.repo).resolve()
    base, _, tip = args.spec.partition("..")
    loc = LOC.match(args.location)
    if not loc or loc["ref"]:
        print(f"error: expected PATH:A-B, got {args.location!r}", file=sys.stderr)
        return 2
    path, a, b = clean_path(loc["path"]), int(loc["a"]), int(loc["b"] or loc["a"])

    new_lines = read_lines(repo, path, tip or None)
    if new_lines is None:
        print(f"error: {path} not found at {tip or 'the working tree'}", file=sys.stderr)
        return 1
    if b > len(new_lines) or a < 1 or b < a:
        print(f"error: {path}:{fmt_range(a, b)} is outside the file ({len(new_lines)} lines)", file=sys.stderr)
        return 1
    try:
        files = diff_files(repo, args.spec, [path])
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        print(f"error: git diff failed: {getattr(exc, 'stderr', '') or exc}", file=sys.stderr)
        return 2
    f = next((f for f in files if f["new"] == path), None)
    old_path = f["old"] if f else path
    if f and not old_path:
        print(f"{path} is new since {base}: there's no Before. Show it as a plain block, not a tabset.")
        return 1
    old_lines = read_lines(repo, old_path, base)
    if old_lines is None:
        print(f"error: {old_path} not found at {base}", file=sys.stderr)
        return 1
    hunks = f["hunks"] if f else []

    if args.old:
        try:
            oa, ob = parse_range(args.old)
        except ValueError:
            print(f"error: --old expects OA-OB, got {args.old!r}", file=sys.stderr)
            return 2
        how = "given with --old"
    else:
        mapped, insert_after = map_to_old(hunks, a, b)
        if mapped:
            oa, ob = min(mapped), max(mapped)
            how = "mapped through the diff"
        else:
            # Pure addition: show the old lines around the insertion point.
            oa, ob = max(1, insert_after - 1), max(1, min(len(old_lines), insert_after + 1))
            how = (f"pure addition after old line {insert_after}: suggested lines around it" if insert_after
                   else "pure addition at the top of the file: suggested first lines")
    if ob > len(old_lines):
        print(f"error: old lines {fmt_range(oa, ob)} are outside {old_path} at {base} ({len(old_lines)} lines)",
              file=sys.stderr)
        return 1
    if not args.old:  # a suggestion never starts or ends on a blank line (Pandoc drops them)
        while oa < ob and not old_lines[oa - 1].strip():
            oa += 1
        while ob > oa and not old_lines[ob - 1].strip():
            ob -= 1

    old_kinds, new_kinds = line_kinds(hunks, old_lines, new_lines)

    def attrs(start, end, kinds, caption):
        marks = fmt_kinds(kinds, range(start, end + 1))
        return f'.numberLines startFrom="{start}"' + (f" {marks}" if marks else "") + f' filename="{caption}"'

    if not hunks:
        print(f"note: {path} has no changes between {base} and {tip or 'the working tree'}")
    print(f"After:  {attrs(a, b, new_kinds, f'{path}:{fmt_range(a, b)}')}")
    print(f"Before: {attrs(oa, ob, old_kinds, f'{old_path}:{fmt_range(oa, ob)}@{base}')}")
    print(f"        ({how})")
    print()
    lo, hi = max(1, oa - args.context), min(len(old_lines), ob + args.context)
    print(f"{old_path} at {base}, lines {fmt_range(lo, hi)} "
          "(> = suggested Before; ~ = changed, - = removed by the diff):")
    width = len(str(hi))
    for n in range(lo, hi + 1):
        flag = (">" if oa <= n <= ob else " ") + {"changed": "~", "removed": "-"}.get(old_kinds.get(n), " ")
        print(f"{flag} {n:>{width}} | {old_lines[n - 1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
