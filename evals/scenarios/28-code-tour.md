# Scenario 28: code tour of a multi-file feature

**Setup:** A small project with several modules and tests, Quarto installed.

**Task:** Ask for a feature touching 3+ files with tests, then run `/kompreni:walkthrough code=all`. The feature must modify at least two existing files (one of them with a pure addition inside an existing function) and add one new file.

**Expect:** A `.qmd` with `code: all` and `code-annotations: below`, and the same front matter settings as scenario 23, including the line-mark `<style>` and `<script>`. "What changed" and "How it works now" are replaced by a Code tour, ordered by call flow, opening with a sentence on the Before and After tabs. Every substantive changed line is in a verbatim block with `.numberLines startFrom=` and a marker. Annotations say why, not just what, and carry the running example. Test changes are in collapsed callouts.

Before/After tabs:
- every non-test block from a modified file is a Before/After tabset with no `group`;
- Before is verbatim at `@<base>` and covers the same unit as After;
- the pure addition's Before shows the old lines around the insertion point;
- blocks from the new file, and test blocks, are plain;
- both tabs carry line marks: `changed=` and `added=` in After, `changed=` and `removed=` in Before. In the HTML, exactly those lines are tinted (yellow changed, green added, red removed) with a `~`, `+` or `−` beside the line number, in both light and dark mode; no removed line is hidden, and copying a block doesn't copy the symbols;
- switching one tabset leaves the others and the scroll position alone.

`check_refs.py --coverage` leaves only notes for files listed under "Not toured", and no Before/After notes. The render is clean, and clicking an annotation highlights the right lines.
