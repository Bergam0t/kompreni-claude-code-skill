# Walkthrough structure

A walkthrough teaches the reader a working mental model of the change: what the code did, what it does now, why, and what to watch. Every section must earn its place. An empty or merely formal section is left out.

## What makes it teach rather than pad

1. **Start from the problem, not the diff.** The reader should know what was wrong or missing before seeing any code.
2. **One running example.** Pick one concrete input, request or scenario that exercises the change. Trace it through the old code in "Before" and through the new code in "How it works now". Use the same example both times, with real names, values and `file:line` references. This is the single most useful device; skip it only when the change has no runtime behaviour (pure docs, config or refactor with identical behaviour, where you say so).
3. **Before and after side by side** for the one to three places where behaviour changed most. In `qmd`, use the Before/After tabset from `formats.md`. In a code tour, every block from a changed file has one (see `code-tour.md`).
4. **Annotate the key code** instead of describing it at length: a short verbatim excerpt with numbered annotations. At most about three annotated excerpts per walkthrough.
5. **A diagram only when the flow or the interaction between components changed.** Never draw a diagram of a single function, or one that restates the file list.
6. **Optional depth goes in collapsed callouts** (`qmd`) or `<details>` (`md`): edge cases, a deep dive into a library, rejected alternatives in detail. Never hide something later sections depend on.
7. **No restating.** Don't list every edit, repeat a section's content in another, or narrate what the agent did ("first I edited..."). Describe behaviour.

## Sections

In this order. Omit any that would be empty. Section headings are `##`, with an id (`{#sec-problem}` and so on) in `qmd`.

| # | Section | Contents |
|---|---|---|
| 1 | **Overview** | The purpose in one paragraph, then an "At a glance" callout: scope (session, branch, commit or range, with SHAs), the main files, the commits, and what the reader will be able to do after reading. Add the drift note here if `dirty: true` |
| 2 | **The problem** | What was wrong, missing or awkward, and who or what it affected. Evidence-labelled |
| 3 | **Before** | How the relevant behaviour worked, traced with the running example. Cite the old code with `@<base>` snippets or references |
| 4 | **Concepts used here** | Per `levels.md`. Not at `advanced`. In `qmd`, each concept may be a short callout |
| 5 | **What changed** | One `###` per purpose group: the behaviour before and after, and the key `file:line` references. Tests go with the code they test. Housekeeping (renames, formatting, lockfiles) in one closing line |
| 6 | **How it works now** | The running example traced through the new code, with annotated excerpts and the Before/After comparison |
| 7 | **How the pieces fit together** | How the changed components interact with each other and with the existing code. The diagram, if one is warranted |
| 8 | **Decisions and alternatives** | Each important decision: what was chosen, the alternatives known to have been considered, and why, each labelled with its evidence. If no reason is recorded, say so |
| 9 | **Verification** | Tests added or changed, tests actually run and their results (or CI results in history mode), and the untested parts named as gaps. If nothing was run, say "Nothing was run." |
| 10 | **Limitations and knock-on effects** | What could break, assumptions, anything now inconsistent elsewhere, follow-up work |
| 11 | **Check your understanding** | See below. Left out with `quiz=off` |
| 12 | **Worth remembering** | Two to four takeaways for the mental model of this codebase, such as "if you change X, also update Y" |
| 13 | **Useful elsewhere** | What this change teaches that holds outside it: library gotchas met here, patterns worth reusing, techniques that worked. Only items that pass the test in `<explain>/references/useful-elsewhere.md`; left out if none do. Link each to the section or stop where it shows up (`@sec-…` in `qmd`). Also listed in the front matter as `kompreni.lessons` |
| 14 | **Scope and provenance** | The resolved range and what was excluded (history mode's scope note), changes present but not made in this session, the snapshot (session mode), and whether a PR was found |

### Short walkthroughs (standard-sized changes)

Merge 2 into 1, merge 6 into 5 (trace the example within each group), and fold 7 into 6 unless there is a diagram. Keep 3, 8, 9, 10, 13 (if anything qualifies) and 14. One or two questions in 11.

## Length

| Size | Words (excluding code, concepts, questions and front matter) |
|---|---|
| Short | about 800-1200 |
| Full | about 1500-2500 |

Above the band, cut repetition first, then move optional detail into collapsed callouts. A large range in history mode follows history-mode.md: say what is covered in depth and what is only summarised, and suggest `focus=`.

## Level

Apply `levels.md` throughout, as in explain: it sets the concepts section, the tone, the analogies and the excerpt lengths. At `new-to-programming`, follow each excerpt with a plain reading of what it does. State the level in the "At a glance" callout.

## Check your understanding

Two to four questions (one or two in a short walkthrough), scaled to the level:

| Level | Questions |
|---|---|
| `new-to-programming` | One recall ("what is X for?"), one trace of the running example ("what happens to <input> now?"), one "what would happen if...?" |
| `new-to-language`, `intermediate` | Predict the behaviour of a shown snippet for a given input; name an edge case and where it is handled; "where would you change...?" (a file and symbol) |
| `advanced` | Scenario questions: what happens under a stated load, failure or later change, and why the design copes or doesn't |

Rules:
- **Ask only what the walkthrough teaches.** Every question is answerable from the document and the code it cites. No trivia about names or line numbers.
- **Answers are verified** against the code. Never invent output. If the code doesn't determine the answer, drop the question.
- **Answers are short** (one to three sentences), point back to the section that covers them, and add no new facts.
- Each answer is hidden until the reader opens it (see `formats.md`), so the reader can try first.

## Standing alone

- Never refer to the conversation ("as discussed", "you asked me to"). The reader may not be the person who was in it.
- Turn *(stated)* rationale into a decision: "*(stated)* Retries are capped at three so a dead server doesn't block the queue." Don't quote the user.
- No personal details: names, email addresses, local paths outside the repo, tokens. The document is likely to be committed and shared.
- Refer to the agent's work neutrally ("this change"), not "I".
