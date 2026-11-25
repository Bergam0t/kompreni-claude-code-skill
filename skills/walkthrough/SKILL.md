---
name: walkthrough
description: Write a structured, persistent walkthrough document (Quarto .qmd, or Markdown) that teaches how and why code changed, for substantial changes worth keeping a record of. Works on the changes an AI agent made in this session, or on a git branch, a commit, or the commits since a ref. Use when the user asks for a walkthrough, write-up or document of changes ("write a walkthrough of this", "document what changed on this branch as a qmd"). For a quick explanation in the chat, use kompreni:explain instead. Never run it automatically after a task.
argument-hint: "[depth=standard|deep] [level=new-to-programming|new-to-language|intermediate|advanced|<free text>] [branch=<name> [onto=<ref>] | since=<ref> | commit=<ref>] [focus=<path or topic>] [scope=all|new] [code=key|all] [format=qmd|md] [out=<dir>] [render=auto|yes|no] [quiz=on|off] [title=\"...\"]"
---

# Kompreni: write a walkthrough of the changes

Write a document that someone who wasn't in this conversation can read, months later, to understand how and why this part of the codebase changed. It is a guided explanation, not a change report and not a restated diff.

This skill shares its change collection, grouping, evidence rules, levels and checker with the explain skill. `<explain>` below is the explain skill's folder: `${CLAUDE_PLUGIN_ROOT}/skills/explain` in a plugin install, otherwise the `explain` folder next to this skill's folder. `<skill>` is this skill's folder.

## 1. Parse arguments

`$ARGUMENTS` is optional `key=value` pairs.

| Arg | Default | Notes |
|---|---|---|
| `depth` | auto | `standard` (a short walkthrough) or `deep` (a full one). See step 4 |
| `level` | auto | As in explain: see `<explain>/references/levels.md` |
| `branch`, `onto`, `since`, `commit` | none | History mode, as in explain. At most one of `branch`, `since` and `commit` |
| `focus` | none | A path or topic. Cover only the changes relevant to it |
| `scope` | `all` | Session mode only. `all`: everything this conversation changed. `new`: only what changed since the last Kompreni explanation or walkthrough in this conversation |
| `code` | `key` | `key`: one to three key excerpts, as in `references/structure.md`. `all`: a **code tour** showing all the substantive changed code with a little context, explained line by line with Quarto code annotations. See `references/code-tour.md`. Implies `format=qmd` |
| `format` | auto | `qmd` or `md`. Auto: `qmd` if `quarto --version` works or a `_quarto.yml` exists in the repo root or a parent folder, otherwise `md` |
| `out` | `kompreni/walkthroughs` | The folder to write into, relative to the repo root |
| `render` | `auto` | `qmd` only. `auto`: render to HTML if Quarto is installed and the file isn't inside an existing Quarto project. `yes`: render anyway. `no`: don't render |
| `quiz` | `on` | `off` leaves out "Check your understanding" |
| `title` | from the changes | The document's title |

**`code=all` with `format=md`** conflict: GitHub-flavoured Markdown has no code annotations. Say so and ask which the user wants. With `code=all` and no Quarto installed, still write `.qmd` (it's readable as text) and skip rendering.

## 2. Collect the changes

Read `<explain>/SKILL.md` and follow its step 2 (session mode) or, in history mode, `<explain>/references/history-mode.md` sections 1-4. That includes taking the snapshot in session mode. Differences:

- The default scope is `all`. With `scope=new`, a previous walkthrough's `Kompreni snapshot:` line counts as a baseline like an explanation's.
- **Uncommitted changes** (session mode with a dirty tree, or `since=` with uncommitted work you are including): step 4 asks whether to commit them first. If they stay uncommitted, write the walkthrough anyway, but references then point at the working tree as it is now and will drift once the code changes. Record `dirty: true` (see `references/front-matter.md`) and put the drift note from `references/formats.md` at the top of the document.

Then read for context and group by purpose, as in explain's steps 3 and 4.

## 3. Nothing to write

If nothing changed, say so and stop. Write no file.

## 4. Before writing: size, and uncommitted changes

Both checks below may need to ask the user something. If both do, ask in one message, and write nothing until they answer.

### Size

Decide the size by explain's rules in `<explain>/references/output-guide.md` ("Choosing the depth"), unless `depth` was given.

- **brief-sized** (one small group, no interface change): a walkthrough isn't worth it. Say so in one line, give the explain command that would cover it, and ask whether to write one anyway. Write it only if the user says yes, then as a short walkthrough.
- **standard**: a short walkthrough.
- **deep**: a full walkthrough.

Length bands and which sections merge in a short walkthrough are in `references/structure.md`.

### Uncommitted changes: offer to commit first

This applies when the walkthrough would cover uncommitted changes (see step 2). It never applies with `branch=` or `commit=`. Skip it if the user has already said whether to commit, for example "write it up, but don't commit".

Ask whether to commit first, with the reason in a sentence or two, and what you would commit, so that one "yes" is enough. For example:

> These changes aren't committed yet. Shall I commit them first? A walkthrough tied to a commit keeps its line references and code excerpts checkable later, can link to the code on GitHub once pushed, and doesn't need a warning that its references may have drifted. I'd commit `src/upload.py` and `tests/test_upload.py` as "Retry failed uploads with backoff". Otherwise I'll write it against the working tree, with that warning.

- **What to commit**: only the changes this walkthrough covers that this session made. Name the user's own uncommitted work (explain's attribution check) separately, and leave it out unless the user asks for it to be included. Stage the named paths only, never `git add -A` or `git add .`.
- **The message**: follow the repository's conventions (recent `git log`, and any rules in CLAUDE.md or contributing docs, such as required trailers or committing on a branch). The summary line says what the change does.
- **On yes**:
    - Note the current `HEAD` first: if the session made no earlier commits, it is the `base`.
    - Stage the paths and commit. Don't push. Never skip hooks (`--no-verify`).
    - If the commit fails, for example because a hook rejects it, report the error in a line or two and ask whether to fix it or to write the walkthrough uncommitted.
    - After the commit, the walkthrough is `dirty: false` and its `tip` is the new commit, which is listed in `commits`. Run the checker in step 7 with `--ref HEAD`, and take a fresh snapshot for the reply's snapshot line.
- **On no**: write it with `dirty: true` and the drift note, and don't suggest committing again in the reply.

## 5. Choose the file

- **Format**: from `format`, or detected as in the table.
- **Name**: `<out>/<YYYY-MM-DD>-<slug>.<qmd|md>`. Use today's date. The slug is 3-6 lowercase words, hyphenated, naming the purpose ("retry-failed-uploads"), not the files.
- **Never overwrite.** If the file exists, add `-2`, `-3` and so on.
- **.gitignore**: when writing `qmd` into a folder with no `.gitignore`, create one there containing `*.html` and `*_files/`, so rendered output isn't committed by accident. Don't edit an existing `.gitignore`.
- Create no other files.

## 6. Write

Read these before writing:
- `references/structure.md`: the sections, the teaching devices, the length bands and the questions.
- `references/formats.md`: the exact syntax for `qmd` and `md`, code snippets and references.
- `references/front-matter.md`: the metadata block at the top.
- `references/code-tour.md`, **only with `code=all`**: it replaces "What changed" and "How it works now" with an annotated code tour, and changes the front matter.
- `<explain>/references/levels.md`: how much language background to give.
- `<explain>/references/useful-elsewhere.md`: the "Useful elsewhere" section.
- `<explain>/references/output-guide.md`, "Evidence labels" and "Code snippets and references".

Non-negotiable rules, as in explain:
- **Label rationale by evidence**: *(code)*, *(stated)*, *(commit `sha`)*, *(PR #n)*, *(observed)* or *(inferred)*. Never invent motives or history.
- **Verification is honest.** Report only tests actually run, with their real results. Name untested parts as gaps.
- **Quote real code only.** Verbatim excerpts carry their location; anything else is marked illustrative.
- **The document stands alone.** The reader doesn't have this conversation. Never copy the user's chat messages into the document, and never include personal details: it is likely to be committed.

## 7. Verify

Never present a walkthrough with unchecked references, snippets or answers.

1. Re-read each cited `file:line` and each quoted snippet against the code. In history mode, read files at the tip with `git show <tip>:<path>`.
2. Run the checker on the file:
   ```
   python <explain>/scripts/check_refs.py --repo . --file <the walkthrough>
   ```
   Add `--ref <tip>` in history mode (`HEAD` for `since=`), and `--ref HEAD` if step 4 committed the changes. Fix every `ERROR` and every `warning`, and re-run until it passes. If Python isn't available, check by hand and say so in the reply.

   In a `.qmd`, the checker also checks code annotations: every marker has its list item, nothing comes between a block and its list, and no item has a second paragraph. Quarto gets these wrong silently.

   With `code=all`, also pass `--coverage <base>..<tip>`. In history mode, `<tip>` is the tip ref. In session mode, use the snapshot's tree as `<tip>`, so untracked files count. Then deal with every `note:` as `references/code-tour.md` says ("Checking coverage").
3. Re-check every answer in "Check your understanding" against the code it relies on. If the code doesn't determine an answer, drop the question.
4. **Render** (`qmd` only, unless `render=no`):
   - If a `_quarto.yml` exists in the walkthrough's folder or any parent, the file belongs to that Quarto project, and rendering sends the HTML to the project's output folder. With `render=auto`, don't render; say why in the reply. With `render=yes`, render and report where the HTML went.
   - Otherwise run `quarto render <file> --to html` from the repo root. The front matter makes the HTML a single self-contained file next to the `.qmd`. Fix anything Quarto warns about and render again until it is clean.
   - If Quarto isn't installed, skip this and say so.

The checker confirms only that quoted code and references exist and match. It can't tell whether your explanation of them is right. Re-read your claims about behaviour against the code you cite.

## 8. Reply in the chat

Keep it short:
- the path of the walkthrough, and of the HTML if rendered (or why it wasn't);
- its depth and level, and two or three sentences on what it covers;
- the commit made in step 4 (short SHA and summary line), if any, or the drift note, if `dirty: true`;
- the checker result, in one line;
- in session mode, end with the line `Kompreni snapshot: tree=<sha> head=<sha>` (the snapshot you took), so that a later explanation or walkthrough covers only what changed after this one.

Don't paste the document into the chat. Don't commit the walkthrough itself; the user decides that.
