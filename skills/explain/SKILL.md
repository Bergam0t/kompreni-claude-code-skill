---
name: explain
description: Explain code changes in depth, covering what changed, why, how the changed pieces interact with the existing code, and what to watch for. Works on the changes an AI agent made in this session, or on the changes on a git branch, in a commit, or since a commit. Use when the user asks for a deeper explanation of changes ("explain what you changed", "walk me through these changes", "explain this branch", "what did commit abc123 do?", "explain everything since v1.2"). Not for routine completion summaries; never run it automatically after a task.
argument-hint: "[depth=brief|standard|deep] [branch=<name> [onto=<ref>] | since=<ref> | commit=<ref>] [focus=<path or topic>]"
---

# Kompreni: explain the changes

Help the user understand not just what changed, but how and why their codebase evolved. Write the explanation **in the conversation**. Create no files.

This is not a restatement of your completion summary. Explain relationships, decisions and consequences the summary skipped.

## 1. Parse arguments

`$ARGUMENTS` is optional `key=value` pairs.

| Arg | Default | Notes |
|---|---|---|
| `depth` | auto | `brief`, `standard` or `deep`. See `references/output-guide.md` for how auto picks |
| `branch` | none | Explain what this branch adds over the default branch |
| `onto` | default branch | With `branch`: the branch to compare against |
| `since` | none | Explain the commits after this ref, up to HEAD |
| `commit` | none | Explain this one commit |
| `focus` | none | A path or topic. Explain only the changes relevant to it |

Give at most one of `branch`, `since` and `commit`. If more than one is given, ask which was meant.

**Modes.** With none of them, this is **session mode**: explain the changes made in this conversation (steps 2-6 below). With one of them, this is **history mode**: read `references/history-mode.md` now. It replaces step 2 and adjusts step 6.

## 2. Collect the changes (session mode)

Git is the source of truth for **what** changed (it catches edits made through Bash, scripts and codegen). This conversation is the source for **why**.

Run, in one Bash call: `git status --porcelain`, `git diff --stat HEAD`, and `git log --oneline -n 10`. Then:

- Untracked files are changes too: read the new ones.
- If this conversation committed, the baseline is the commit before the first one it made. Confirm with `git log`.
- **Attribution check.** Compare git's file list with the files this conversation edited, created or ran commands against. Changes the session did not make (the user's own uncommitted work) go in a separate "Not from this session" note, and are never explained as your work. If you can't tell, say so.
- **Large diffs**: read the stat first, then diffs one group at a time. Summarise lockfiles, generated code and pure formatting in a single line.
- **No git repo**: fall back to what this conversation edited, and state that coverage may be incomplete.
- **Nothing changed**: say so and stop.
- If the conversation was compacted, git stays authoritative. Say where intent is reconstructed.

## 3. Read for context, within a budget

For each changed function or interface, look at its callers, callees and covering tests, enough to explain how the parts interact. Don't read the whole repository.

## 4. Group by purpose

Group by behaviour or capability, not by file. Tests go with the code they test. Renames, moves and formatting go in one "housekeeping" line. A file can appear in more than one group.

## 5. Pick the depth and write

Read `references/output-guide.md` for the depth rules, the section structure, the evidence labels and the style limits. `references/examples.md` has one illustrative example per depth.

Non-negotiable rules:

- **Label rationale by evidence**: *(code)* the diff or code shows it, *(stated)* it was said in this conversation, *(inferred)* your reasoning. Never invent motives or history.
- **Verification is honest.** Report only tests actually run in this conversation, with their real results. Name untested parts as gaps.
- **Be proportionate.** A small fix gets a short explanation. Don't pad.
- **Quote real code only.** Short excerpts, copied exactly from the diff or the file, each tagged with its location. Anything simplified or invented is marked `illustrative`. See the snippet rules in `references/output-guide.md`.
- Link files and lines with real references (`[file.py:42](path/file.py#L42)` in the IDE; `path/file.py:42` in a terminal).

## 6. Verify before you answer

Never present a draft with unchecked references or snippets.

1. Re-read each cited `file:line` and each quoted snippet against the working tree (or `git show <ref>:<path>` for "before" code). Line numbers drift after edits, so take them from the files, not from memory.
2. Run the checker, passing the draft on stdin so that no file is created. In history mode, add `--ref <tip>` (see `references/history-mode.md`):

```
python <skill>/scripts/check_refs.py --repo . <<'DRAFT'
<the draft explanation>
DRAFT
```

   (`<skill>` is the folder containing this SKILL.md, in a plugin install `${CLAUDE_PLUGIN_ROOT}/skills/explain`. Use `python3` if `python` isn't found.)
3. Fix every `ERROR` (a mismatched snippet, a missing file, a line outside the file) and re-run until it passes. Treat a `warning` about an unmarked code block as an error too: add a location, or mark it `illustrative`.
4. If Python isn't available, do step 1 by hand and add one line to the explanation saying the references were checked manually, not by script.

The checker confirms only that quoted code and references exist and match. It cannot tell whether your explanation of them is right. Re-read your claims about behaviour against the code you cite.
