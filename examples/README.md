# Examples

The same change, explained three ways. The change is three commits that sped up a discrete-event simulation (SimPy and pandas) by building its lookups once instead of filtering DataFrames in every loop.

| | Source | Rendered |
|---|---|---|
| Explanation (`/kompreni:explain since=… depth=deep`) | [explain.md](explain.md) | GitHub renders it directly |
| Walkthrough (`/kompreni:walkthrough since=… depth=deep`) | [walkthrough.qmd](walkthrough.qmd) | [walkthrough.html](https://bergam0t.github.io/kompreni-claude-code-skill/examples/walkthrough.html) |
| Code tour (`/kompreni:walkthrough code=all`) | [code-tour.qmd](code-tour.qmd) | [code-tour.html](https://bergam0t.github.io/kompreni-claude-code-skill/examples/code-tour.html) |

They were written in another repository, [ReModel-Club/MOOOD-study](https://github.com/ReModel-Club/MOOOD-study/tree/add-codebase-tutorial) (branch `add-codebase-tutorial`), covering commits `4188308..8a5fc92`. Their `file:line` references and the `kompreni/walkthroughs/…` paths they mention point into that repository, not this one. The files are otherwise unedited, apart from their names.
