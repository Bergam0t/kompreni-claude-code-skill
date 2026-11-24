# kompreni-offer (optional mod)

An optional companion to the `kompreni` skill. After a turn in which Claude edited files, it shows one row above the prompt:

```
Kompreni: 3 files changed since the last explanation.  Depth [auto ▾]  Level [new-to-language ▾]  [Explain]  [Dismiss]
```

The count matches what the skill will explain: files edited since the last Kompreni explanation in this session, across however many turns. It resets when an explanation actually runs, whether you used the button, typed the command, or asked Claude in words. History-mode runs (`branch=`, `since=`, `commit=`) don't reset it. **Dismiss** hides the row until the next turn that edits something; the count carries on.

**Explain** fills your prompt box with the command, e.g. `/kompreni:explain depth=deep level=new-to-language`. You press Enter. It never submits for you, and it never overwrites a draft you've started.

The depth and level you pick are remembered across sessions.

## Requirements

- Claude Code with mod support (built and tested against 2.1.331).
- The Kompreni explain skill, as the `kompreni` plugin (`/kompreni:explain`) or as a plain skill named `kompreni-explain`. The mod finds whichever is installed.

## Load it

- **CLI, for trying it:** `claude --plugin-dir <this folder>` (add another `--plugin-dir` for the skill if it isn't installed).
- **Installed:** `/plugin install kompreni-offer@kompreni` from this repository's marketplace.

## Settings: `/kompreni-offer`

```
/kompreni-offer                                   # show current settings
/kompreni-offer off                               # stop offering (on to resume)
/kompreni-offer depth=brief
/kompreni-offer level="fluent in R, new to Python"
/kompreni-offer command=kompreni-explain          # force which skill command to use
```

A free-text level set here appears as an extra option in the Level picker.

## Limitations

- It notices edits made with Claude's Edit, Write and NotebookEdit tools, including by subagents. A turn that changed files **only** through shell commands won't trigger an offer. You can still run the skill yourself, and it reads the real changes from git either way.
- Offers appear only after the main conversation's turns finish with an answer, not after interrupted turns.
- Mods are a new, evolving part of Claude Code and are not sandboxed. Read `hooks/register.tsx` before loading it.

## Development

- `claude plugin validate .`
- `claude plugin test .` runs `tests/register.test.tsx`
- Type-check: Claude Code writes the API types into `.claude-plugin/types/` when it loads the mod, after which `tsc -p .` works.
