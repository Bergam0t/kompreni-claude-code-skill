"""Pre-render step for the docs site.

Copies and converts files that live outside site/ into gitignored paths
inside it, so Quarto can use them:

- ../examples/{walkthrough,code-tour}.html -> examples/ (verbatim, so the
  /examples/*.html URLs keep working)
- ../mods/kompreni-offer/images/*.png -> images/mod/
- ../examples/explain.md -> _generated/explain.qmd, converted so it can sit
  inside a Quarto tab (see convert_explain)

Standard library only. Safe to run repeatedly.
"""

import re
import shutil
from pathlib import Path

SITE = Path(__file__).resolve().parent
REPO = SITE.parent

# ```python hsm.py:386@4188308  ->  language "python", location "hsm.py:386@4188308"
FENCE = re.compile(r"^```([A-Za-z0-9_+-]+)\s+(\S+)\s*$")
HEADING = re.compile(r"^(#{1,6})(\s)")
LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s")
EXAMPLE_NOTE = re.compile(r"^>\s*\*An example of .*\*\s*$")


def convert_explain(text: str) -> str:
    """Make explain.md safe to include inside a Quarto tabset.

    - Pandoc's markdown reader turns ```lang path:lines fences into inline
      code, so rewrite them to ```{.lang filename="path:lines"}, which also
      shows the location as a caption.
    - Demote headings by two levels so they sit below the tab headings (##).
    - Drop the "An example of ..." note, which is for readers on GitHub.
    - Put a blank line before a list that follows a line of text. GFM
      starts the list anyway; pandoc's markdown would merge it into the
      paragraph.
    """
    out = []
    in_code = False
    for line in text.splitlines():
        if (not in_code and LIST_ITEM.match(line) and out
                and out[-1].strip() and not LIST_ITEM.match(out[-1])
                and not out[-1].startswith((" ", "\t"))):
            out.append("")
        if line.startswith("```"):
            if not in_code:
                m = FENCE.match(line)
                if m:
                    line = f'```{{.{m.group(1)} filename="{m.group(2)}"}}'
            in_code = not in_code
        elif not in_code:
            if EXAMPLE_NOTE.match(line):
                continue
            line = HEADING.sub(lambda m: "#" * min(len(m.group(1)) + 2, 6) + m.group(2), line)
        out.append(line)
    return "\n".join(out).lstrip("\n") + "\n"


def main() -> None:
    examples = SITE / "examples"
    examples.mkdir(exist_ok=True)
    for name in ("walkthrough.html", "code-tour.html"):
        shutil.copy2(REPO / "examples" / name, examples / name)

    images = SITE / "images" / "mod"
    images.mkdir(parents=True, exist_ok=True)
    for png in (REPO / "mods" / "kompreni-offer" / "images").glob("*.png"):
        shutil.copy2(png, images / png.name)

    generated = SITE / "_generated"
    generated.mkdir(exist_ok=True)
    explain = (REPO / "examples" / "explain.md").read_text(encoding="utf-8")
    (generated / "explain.qmd").write_text(convert_explain(explain), encoding="utf-8")


if __name__ == "__main__":
    main()
