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
/kompreni:explain depth=deep focus=src/api
```

You can also just ask, for example "walk me through what you changed". The skill never runs on its own after every task.

**Several explanations in one conversation.** Each explanation covers only what changed since the previous one, and says how the new changes interact with the earlier ones. Use `scope=all` for one consolidated explanation of everything the conversation changed, e.g. before committing. To make "since the previous one" reliable, each explanation ends with a line like `Kompreni snapshot: tree=4f2a91c… head=51d0a3b…`. That's a git snapshot of your working tree, taken without changing your files, index, branches or stash. Its only side effect is unreferenced objects inside `.git`, which git cleans up in time. Untracked files over 5 MB are left out of it.

### Matching your experience

```
/kompreni:explain level=new-to-language
/kompreni:explain level="fluent in R, new to Python"
```

`level` sets how much language and library background is explained alongside the change:
- `new-to-programming` (or `beginner`): general programming concepts as well as the language;
- `new-to-language`: syntax, idioms, gotchas and libraries, for experienced programmers;
- `intermediate` (the default): only less-common features;
- `advanced`: no background at all;
- or describe yourself in free text, and new constructs are explained by comparison with what you know.

If you don't give a level, Kompreni uses what you've told Claude about your experience (in the chat, `CLAUDE.md` or memory). The level used is named in the first line, so you can correct it.

### Explaining history: a branch, a commit, or a range

```
/kompreni:explain branch=feature-x              # what the branch adds over the default branch
/kompreni:explain branch=feature-x onto=develop
/kompreni:explain commit=abc1234
/kompreni:explain since=v1.2.0
```

In history mode the conversation can't say why something was done, so the explanation draws on commit messages, the pull request (if the GitHub CLI `gh` is available) and the code. Each reason is labelled with its source. If the commit sequence shows an approach that was tried and replaced, or fixes made after review, it adds a short "How it got here". The skill never checks out, stashes or resets anything.

### Optional: an offer after each change

The [`kompreni-offer`](mods/kompreni-offer/) mod shows a row above the prompt after any turn that edited files, counting the files changed since the last explanation, with depth and level pickers and an **Explain** button that fills in the command for you. It remembers your choices. The skill works fine without it.

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

- Unit tests for the reference checker and the snapshot script: `python -m unittest discover tests`
- Mod tests: `claude plugin test mods/kompreni-offer`
- Manual scenarios and the scoring rubric: [evals/README.md](evals/README.md)
