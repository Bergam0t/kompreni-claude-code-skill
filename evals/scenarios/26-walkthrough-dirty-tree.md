# Scenario 26: walkthrough of uncommitted changes, declining the commit

**Setup:** Any git project.

**Task:** Ask for a multi-file change, don't commit, run `/kompreni:walkthrough`. When asked whether to commit first, say no.

**Expect:** Before writing anything, one short question: commit first?, with the reason in a sentence or two, the files it would commit and a draft message. After "no": the walkthrough is written, with `dirty: true` in the front matter and the "References point at uncommitted code" note at the top naming the head SHA. No permalinks. Nothing was committed, and the reply doesn't suggest committing again.
