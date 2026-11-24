# Scenario 10: one commit, then a merge commit

**Setup:** A repo with a normal commit with a descriptive message, and a merge commit.

**Task:** Run `commit=<normal sha>`, then `commit=<merge sha>`.

**Expect:** The first is labelled *(commit sha)* where the message gives a reason. The second says it is diffed against the first parent.
