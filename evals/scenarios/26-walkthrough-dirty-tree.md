# Scenario 26: walkthrough of uncommitted changes

**Setup:** Any git project.

**Task:** Ask for a multi-file change, don't commit, run `/kompreni:walkthrough`.

**Expect:** The walkthrough is written, with `dirty: true` in the front matter and the "References point at uncommitted code" note at the top naming the head SHA. No permalinks. The reply suggests committing first next time for stable references.
