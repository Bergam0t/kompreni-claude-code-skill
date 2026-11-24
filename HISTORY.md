# 0.1.0

- Add `/kompreni:explain`, a Claude Code skill that explains an agent's changes in the conversation
    - Collects changes from git and the conversation, and separates changes the session didn't make
    - Groups changes by purpose and picks a brief, standard or deep explanation
    - Labels rationale as code, stated or inferred, and reports only tests actually run
- Check code references and quoted snippets before answering
    - Snippets are copied verbatim with a location tag, or marked `illustrative`
    - `skills/explain/scripts/check_refs.py` fails on missing files, out-of-range lines and snippets that don't match the repo or a git ref
- Explain the changes on a branch, in a commit, or since a commit (history mode)
    - New `branch=` (with `onto=`), `commit=` and `since=` arguments; `base=` is removed
    - Draws rationale from commit messages and the pull request (via `gh`), labelled *(commit)* and *(PR #n)*
    - Adds an optional "How it got here" section and a scope note; never changes the checkout
    - Handles already-merged branches (finds the merge commit via the PR) and branch names that are also file names
    - `check_refs.py --ref <git-ref>` checks references against a branch or commit that isn't checked out
