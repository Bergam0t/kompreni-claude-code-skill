# Scenario 23: full walkthrough as Quarto

**Setup:** A small project with several modules and tests, Quarto installed, no `_quarto.yml`.

**Task:** Ask for a feature touching 3+ files with tests, run the tests, then run `/kompreni:walkthrough`.

**Expect:** Writes `kompreni/walkthroughs/<date>-<slug>.qmd` and a `.gitignore` beside it. One running example traced through the old and new code; a Before/After tabset; at most about three annotated excerpts; a diagram only if the flow changed. Questions are answerable from the document, with answers that match the code. `check_refs.py` passes on the file, `quarto render` is clean, and the HTML is a single file. The front matter has the `grid`, the light/dark `theme`, `respect-user-color-scheme: true` and the theme-fix `<style>` from `front-matter.md`: the HTML opens in the system colour scheme and has a toggle in the top right, and any diagram is readable in both modes. The front matter is complete and its SHAs and file list are right. The reply ends with a snapshot line, and a following `/kompreni:explain` covers only later changes.
