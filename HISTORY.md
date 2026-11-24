# 0.1.0

- Add `/kompreni:explain`, a Claude Code skill that explains an agent's changes in the conversation
    - Collects changes from git and the conversation, and separates changes the session didn't make
    - Groups changes by purpose and picks a brief, standard or deep explanation
    - Labels rationale as code, stated or inferred, and reports only tests actually run
- Check code references and quoted snippets before answering
    - Snippets are copied verbatim with a location tag, or marked `illustrative`
    - `skills/explain/scripts/check_refs.py` fails on missing files, out-of-range lines and snippets that don't match the repo or a git ref
