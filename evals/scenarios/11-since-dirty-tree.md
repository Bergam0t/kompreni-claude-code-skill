# Scenario 11: since a ref, with uncommitted work

**Setup:** Tag a commit, add 3 commits after it, then leave an uncommitted edit.

**Task:** Run `since=<tag> depth=brief`.

**Expect:** Explains the 3 commits only. The scope note says uncommitted work isn't included. The checker ran with `--ref HEAD`.
