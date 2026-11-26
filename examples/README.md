# Examples

The same change, explained three ways. To switch between them in tabs, see [Compare the three outputs](https://bergam0t.github.io/kompreni-claude-code-skill/compare.html) on the docs site. The change is three commits that sped up a discrete-event simulation (SimPy and pandas) by building its lookups once instead of filtering DataFrames in every loop.

| | Source | Rendered |
|---|---|---|
| Explanation (`/kompreni:explain since=… depth=deep`) | [explain.md](explain.md) | GitHub renders it directly |
| Walkthrough (`/kompreni:walkthrough since=… depth=deep`) | [walkthrough.qmd](walkthrough.qmd) | [walkthrough.html](https://bergam0t.github.io/kompreni-claude-code-skill/examples/walkthrough.html) |
| Code tour (`/kompreni:walkthrough code=all`) | [code-tour.qmd](code-tour.qmd) | [code-tour.html](https://bergam0t.github.io/kompreni-claude-code-skill/examples/code-tour.html) |

They were written in another repository, [ReModel-Club/MOOOD-study](https://github.com/ReModel-Club/MOOOD-study/tree/add-codebase-tutorial) (branch `add-codebase-tutorial`), covering commits `4188308..8a5fc92`. Their `file:line` references and the `kompreni/walkthroughs/…` paths they mention point into that repository, not this one. The files are otherwise unedited, apart from their names and one fix: the walkthrough and code tour were re-rendered with the dark-mode fix for inline code in code-annotation notes (two CSS lines in their front matter).

`demo.gif`, shown in the main README, is made from the rendered docs site by `site/_make_demo_gif.py`.
