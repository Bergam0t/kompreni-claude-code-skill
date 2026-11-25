# Scenario 28: code tour of a multi-file feature

**Setup:** A small project with several modules and tests, Quarto installed.

**Task:** Ask for a feature touching 3+ files with tests, then run `/kompreni:walkthrough code=all`.

**Expect:** A `.qmd` with `code: all` and `code-annotations: below`, and the same light/dark theme settings as scenario 23. "What changed" and "How it works now" are replaced by a Code tour, ordered by call flow. Every substantive changed line is in a verbatim block with `.numberLines startFrom=` and a marker. Annotations say why, not just what, and carry the running example. Test changes are in collapsed callouts. `check_refs.py --coverage` leaves only notes for files listed under "Not toured". The render is clean, and clicking an annotation highlights the right lines.
