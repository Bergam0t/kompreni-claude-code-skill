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
- Match explanations to the reader's prior knowledge with `level=`
    - Presets: `new-to-programming` (alias `beginner`), `new-to-language`, `intermediate` (default) and `advanced`, or free text such as `"fluent in R, new to Python"`
    - A "Concepts used here" section explains the constructs, patterns and library APIs the change relies on, each tied to a real line
    - With no `level=`, uses what the user has said about their experience, and names the level used
