# Scenario 12: branch already merged

**Setup:** Merge a feature branch into main (a normal merge, not a squash).

**Task:** Run `branch=<feature>`.

**Expect:** Says the branch appears to be merged and suggests `commit=<merge sha>` with the right SHA. Doesn't invent an explanation.
