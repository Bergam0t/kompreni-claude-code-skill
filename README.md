# Kompreni

*Esperanto for "to understand".* Understand what an AI coding agent changed, why it changed, and how it fits into your codebase.

Agent completion summaries tell you what was done. Kompreni helps you build a mental model of how and why your code evolved.

## Status

**v0.1.0:**
- Layer 1, `/kompreni:explain`, explains changes in the conversation and writes no files.
- Layer 2, `/kompreni:walkthrough`, writes a structured Quarto or Markdown walkthrough for changes worth keeping a record of.

Persistent, searchable knowledge (Layer 3) is planned but not built. The walkthroughs' front matter is its starting point. See [HANDOVER-original.md](HANDOVER-original.md).

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

**Lessons that travel.** When a change teaches something beyond itself, a "Useful elsewhere" section says so: a library gotcha the change ran into, a design pattern worth reusing, or a debugging or testing technique that worked. Each item points to where it shows up in this change and is labelled with its evidence. It's left out when there's nothing real to say, which is often.

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

If you don't give a level, Kompreni uses `intermediate`, unless something in this conversation, your `CLAUDE.md` or Claude's memory describes your experience (for example "I'm new to Python"). The level used is named in the first line, so you can correct it.

### Explaining history: a branch, a commit, or a range

```
/kompreni:explain branch=feature-x              # what the branch adds over the default branch
/kompreni:explain branch=feature-x onto=develop
/kompreni:explain commit=abc1234
/kompreni:explain since=v1.2.0
```

In history mode the conversation can't say why something was done, so the explanation draws on commit messages, the pull request (if the GitHub CLI `gh` is available) and the code. Each reason is labelled with its source. If the commit sequence shows an approach that was tried and replaced, or fixes made after review, it adds a short "How it got here". The skill never checks out, stashes or resets anything.

### Walkthroughs: a document worth keeping

For a substantial change, `/kompreni:walkthrough` writes a guided walkthrough to a file instead of the chat. It's for someone reading later, who wasn't in the conversation.

```
/kompreni:walkthrough
/kompreni:walkthrough branch=feature-x level=new-to-language
/kompreni:walkthrough commit=abc1234 format=md
/kompreni:walkthrough code=all            # a code tour: every changed line, annotated
```

- **Where**: `kompreni/walkthroughs/<date>-<slug>.qmd`, meant to be committed. Change the folder with `out=`.
- **Format**: Quarto (`.qmd`) if Quarto is installed, otherwise GitHub-flavoured Markdown (`.md`). Force one with `format=qmd|md`.
- **Rendering**: a `.qmd` is rendered to a single self-contained HTML file next to it, which a `.gitignore` there keeps out of git. If your repo is already a Quarto project, the walkthrough isn't rendered by default, because Quarto would send it into your site's output. Exclude `kompreni/` in your `_quarto.yml` if you don't want walkthroughs on your site.
- **What's in it**:
    - the problem, then one concrete example traced through the code before and after the change;
    - annotated excerpts and before/after tabs;
    - a diagram, only if the flow changed;
    - the decisions with their evidence, honest verification, limitations, and a few questions with hidden answers (`quiz=off` to leave them out);
    - "Useful elsewhere", when the change teaches something that applies beyond it (also listed in the front matter, so these lessons can be searched across walkthroughs later).
- **Code tour** (`code=all`): instead of a few key excerpts, it shows all the substantive changed code, with a little context, in order of the call flow. It uses Quarto code annotations: numbered markers on the lines, with explanations below each block that highlight their lines when clicked. Line numbers match the real files. Test changes are annotated inside collapsed sections, and housekeeping is summarised. A `--coverage` check confirms that every changed line is either shown or listed as not toured. Quarto only.
- **Proportionate**: for a small change it suggests `/kompreni:explain` instead, and asks before writing.
- **Uncommitted changes**: Claude asks whether to commit them first, saying what it would commit and with what message. A walkthrough tied to a commit keeps references that can always be checked and, on GitHub, permalinks. Only the session's own changes are committed, and nothing is pushed. If you say no, the walkthrough notes that its line references point at the working tree as it was, and may drift.
- **Front matter** records the range, commits, files, level and tests (`kompreni:` in the YAML). This is the start of Kompreni's searchable change history.

The skill shares `level=`, `focus=` and history mode with `/kompreni:explain`. It covers the whole conversation by default (`scope=all`).

### Optional: an Explain row above the prompt

The [`kompreni-offer`](mods/kompreni-offer/) mod shows a row above the prompt whenever Claude isn't working (or, with `/kompreni-offer show=changes`, only after turns that edited files). It counts the files changed since the last explanation, and has depth and level pickers and **Explain**, **Walkthrough** and **Code tour** buttons that fill in the command for you. It remembers your choices. The skill works fine without it.

## How it works

- **Git** supplies what changed (including edits made through shell commands). **The conversation** supplies why.
- Changes are grouped by purpose, not file, and the depth (brief, standard or deep) is matched to the size of the change.
- Rationale is labelled *(code)*, *(stated)* or *(inferred)*, so reasons are never invented.
- Quoted code is copied verbatim with its location, or marked `illustrative`. A small script (`skills/explain/scripts/check_refs.py`, Python 3.9+, standard library only) checks every snippet and `file:line` reference against the repo before the explanation or walkthrough is shown. It understands both Markdown and Quarto code blocks, and GitHub permalinks. It can't check that the prose about the code is right.
- Verification reports only tests actually run in the session.
- Changes in git that the session didn't make (your own uncommitted work) are listed separately.

## Relation to codebase-tutorial

[codebase-tutorial](https://github.com/Bergam0t/tutorial-codebase-knowledge-claude-code-skill) explains how a codebase works. Kompreni explains how and why it changed.

## Testing

- Unit tests for the reference checker and the snapshot script: `python -m unittest discover tests`
- Mod tests: `claude plugin test mods/kompreni-offer`
- Manual scenarios and the scoring rubric: [evals/README.md](evals/README.md)
