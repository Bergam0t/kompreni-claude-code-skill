# Scenario 31: walkthrough of uncommitted changes, committing first

**Setup:** Any git project. Before the task, edit an unrelated file yourself and leave it uncommitted.

**Task:** Ask for a multi-file change, don't commit, run `/kompreni:walkthrough`. When asked whether to commit first, say yes.

**Expect:**
- The question names only the session's files, mentions your own edit separately as not included, and gives a draft message that follows the repo's conventions.
- After "yes": one new commit containing exactly the session's files, made with hooks running. Your own edit is still uncommitted. Nothing is pushed.
- The walkthrough has `dirty: false`, `tip` = the new commit, the commit listed in `commits`, and `base` = `HEAD` from before the commit. No drift note.
- `check_refs.py --ref HEAD` passes. The reply names the commit and ends with a snapshot line whose `head` is the new commit.
- Variant: if a pre-commit hook fails, the error is reported and the user is asked whether to fix it or write uncommitted; hooks are never skipped.
