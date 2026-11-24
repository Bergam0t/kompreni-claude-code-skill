# Kompreni

*Esperanto for "to understand".* Understand what an AI coding agent changed, why it changed, and how it fits into your codebase.

Agent completion summaries tell you what was done. Kompreni helps you build a mental model of how and why your code evolved.

## Status

**Layer 1 only (v0.1.0):** a Claude Code skill that explains recent changes in the conversation. No files are written. Structured walkthroughs and persistent knowledge are planned but not built; see [HANDOVER-original.md](HANDOVER-original.md).

## Install

```
/plugin marketplace add <path-or-repo-of-this-project>
/plugin install kompreni@kompreni
```

Or try it locally: `claude --plugin-dir <this folder>`.

## Use

After the agent has made changes:

```
/kompreni:explain
/kompreni:explain depth=deep
/kompreni:explain base=main focus=src/api
```

You can also just ask, for example "walk me through what you changed". The skill never runs on its own after every task.

## How it works

- **Git** supplies what changed (including edits made through shell commands). **The conversation** supplies why.
- Changes are grouped by purpose, not file, and the depth (brief, standard or deep) is matched to the size of the change.
- Rationale is labelled *(code)*, *(stated)* or *(inferred)*, so reasons are never invented.
- Quoted code is copied verbatim with its location, or marked `illustrative`. A small script (`skills/explain/scripts/check_refs.py`, Python 3.9+, standard library only) checks every snippet and `file:line` reference against the repo before the explanation is shown. It can't check that the prose about the code is right.
- Verification reports only tests actually run in the session.
- Changes in git that the session didn't make (your own uncommitted work) are listed separately.

## Relation to codebase-tutorial

[codebase-tutorial](https://github.com/Bergam0t/tutorial-codebase-knowledge-claude-code-skill) explains how a codebase works. Kompreni explains how and why it changed.

## Testing

See [evals/README.md](evals/README.md).
