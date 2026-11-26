# Kompreni

*Esperanto for "to understand".* Understand what an AI coding agent changed, why it changed, and how it fits into your codebase.

Agent completion summaries tell you what was done. Kompreni helps you build a mental model of how and why your code evolved.

**Documentation: [bergam0t.github.io/kompreni-claude-code-skill](https://bergam0t.github.io/kompreni-claude-code-skill/)**, including [the three outputs side by side](https://bergam0t.github.io/kompreni-claude-code-skill/compare.html) on one real change.

## Requirements

- Claude Code.
- A git repository. Without one, Kompreni can only use what the conversation edited, and says that coverage may be incomplete.
- Optional:
    - Python 3.9 or later, to check every quoted snippet and line reference against the repo. Without it, Claude checks by hand and says so.
    - [Quarto](https://quarto.org), for walkthroughs with tabs and code annotations, rendered to HTML. Without it, walkthroughs are Markdown, and code tours are written as `.qmd` but not rendered.
    - The GitHub CLI `gh`, to draw on pull requests when explaining a branch.
    - For the optional mod: a Claude Code version with mod support (tested with 2.1.331).

## Install

```
/plugin marketplace add Bergam0t/kompreni-claude-code-skill
/plugin install kompreni@kompreni
/plugin install kompreni-offer@kompreni    # optional: buttons above the prompt box (a mod)
```

The mod runs as code inside Claude Code and isn't sandboxed, so read [`hooks/register.tsx`](mods/kompreni-offer/hooks/register.tsx) before installing it.

To update: `/plugin marketplace update kompreni`, then `/plugin update kompreni@kompreni` (and `kompreni-offer@kompreni` if you have the mod). To remove: `/plugin uninstall kompreni@kompreni`.

To try it without installing:

```
git clone https://github.com/Bergam0t/kompreni-claude-code-skill
claude --plugin-dir kompreni-claude-code-skill
```

Add `--plugin-dir kompreni-claude-code-skill/mods/kompreni-offer` to try the mod too.

## Quick start

After Claude has changed some code:

```
/kompreni:explain                 # explain the changes in the chat
/kompreni:walkthrough             # write them up as a document to keep
/kompreni:walkthrough code=all    # a code tour: every changed line, annotated
```

Or just ask: "explain what you changed" gives you an explanation, and "write a walkthrough of this" gives you the document. Neither runs on its own after a task.

## Which one?

|  | Explain | Walkthrough | Code tour |
|---|---|---|---|
| **Command** | `/kompreni:explain` | `/kompreni:walkthrough` | `/kompreni:walkthrough code=all` |
| **Output** | An answer in the chat; no files | A `.qmd` or `.md` file, rendered to HTML, meant to be committed | Same as a walkthrough, always `.qmd` |
| **Code shown** | Short verbatim snippets | One to three key excerpts, with before/after comparisons | All the substantive changed code, annotated line by line, with Before/After tabs |
| **Use when** | You want to understand a change now | A substantial change deserves a record for someone reading later: a reviewer, a teammate, or you in six months | You, or a reviewer, want to understand every changed line from the code itself |
| **Example** | [Explain](https://bergam0t.github.io/kompreni-claude-code-skill/compare.html#explain) | [Walkthrough](https://bergam0t.github.io/kompreni-claude-code-skill/compare.html#walkthrough) | [Code tour](https://bergam0t.github.io/kompreni-claude-code-skill/compare.html#code-tour) |

All three examples cover the same real change. Their sources are in [examples/](examples/).

## More in the documentation

- [Usage](https://bergam0t.github.io/kompreni-claude-code-skill/usage.html): several explanations in one conversation, matching your experience (`level=`), explaining a branch, commit or range, what a walkthrough changes in your repo, and **all options**.
- [The kompreni-offer mod](https://bergam0t.github.io/kompreni-claude-code-skill/mod.html): the buttons above the prompt, with screenshots, settings and limitations.
- [How it works](https://bergam0t.github.io/kompreni-claude-code-skill/how-it-works.html): evidence labels, checked references, snapshots and Before/After marks.

## Testing

- Unit tests for the reference checker, the snapshot script and the Before-range script: `python -m unittest discover tests`
- Mod tests: `claude plugin test mods/kompreni-offer`
- Manual scenarios and the scoring rubric: [evals/README.md](evals/README.md)
- Docs site: `cd site && python _prepare.py && quarto render` (or `quarto preview`). It deploys from main through [.github/workflows/site.yml](.github/workflows/site.yml).

## Roadmap

Version 0.1.0. Next: persistent knowledge that can be searched across walkthroughs, starting from their front matter. See [HANDOVER-original.md](HANDOVER-original.md).
