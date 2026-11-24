# Output guide

## Choosing the depth

If `depth` wasn't given, pick from the grouped changes:

| Depth | When | Length |
|---|---|---|
| **brief** | One group, a small diff, no change to a public interface or data format | 3-6 sentences, about 120 words |
| **standard** | Everything in between (the default when unsure) | About 500 words |
| **deep** | Several interacting groups, an architecture or interface change, a migration, or concurrency or security implications | Up to about 1000 words |

State the depth and the level (see `levels.md`) in a few words at the start, so the user can ask for more or less.

## Standard structure

Omit any section that would be empty.

1. **In one paragraph**: the purpose of the changes and the problem they address.
2. **Concepts used here** (not at `advanced`, and only when something qualifies): the language constructs, patterns and library APIs the reader needs in order to follow the change. See `levels.md`. Its words don't count towards the length limit.
3. **What changed, by purpose**: per group, what the code did before, what it does now, and the key file:line references. Describe behaviour, not edits.
4. **Why it was done this way**: the important decisions, and the alternatives where they are known. Label each with its evidence: *(code)*, *(stated)*, *(commit `sha`)*, *(PR #n)* or *(inferred)*.
5. **How the pieces fit together**: how the changed components interact with each other and the existing code.
6. **Limitations and knock-on effects**: what could break, assumptions made, anything now inconsistent elsewhere.
7. **Verification**: tests added or changed, and tests actually run in this conversation with their real results. Name untested parts as gaps. If nothing was run, say "nothing was run". In history mode, report the PR's CI results instead (see `history-mode.md`).
8. **How it got here** (history mode only, optional): what the commit sequence shows that the final diff hides. See `history-mode.md`.
9. **Worth remembering**: 2-3 takeaways for the reader's mental model, such as "if you change X later, also update Y".
10. **Not from this session** (session mode): changes present in git that this conversation didn't make, if any. In history mode this is the **Scope** note instead: the resolved range, what was excluded, and whether a PR was found.

## Brief

A short paragraph: purpose, before and after, why (labelled if it isn't obvious), and verification. No headings. Instead of a concepts section, gloss at most two concepts in parentheses at first mention (see `levels.md`).

## Deep

Standard, plus a small ASCII flow in "How the pieces fit together" when it clarifies an interaction. End with one line saying a structured walkthrough could be worth writing for a change this size. Don't offer to generate one yet; that feature doesn't exist.

## Evidence labels

- *(code)*: visible in the diff or the surrounding code. Cite where.
- *(stated)*: said by the user or you earlier in this conversation.
- *(commit `abc1234`)*: from that commit's message. It's the author's claim, not verified fact.
- *(PR #n)*: from that pull request's description or review comments.
- *(inferred)*: your reasoning from the above. Say "probably" or "presumably". If you have no basis at all, say the reason isn't recorded.

Don't attribute intent without one of these.

## Code snippets and references

Prefer a short excerpt over a long description when the code is the clearest explanation, for example the key changed lines or a before/after pair. Don't quote what prose says better.

- **Verbatim snippets**: copied exactly from the diff or the file, at most about 15 lines. Put the location in the fence's info string, after the language: `python src/api.py:40-46`. For code as it was before the change, add the ref: `python src/api.py:40-46@HEAD`. In a Markdown fence this reads:

  ````
  ```python src/api.py:40-46
  <the exact lines>
  ```
  ````

- **Illustrative snippets**: simplified, abridged, or showing a suggested alternative. Put `illustrative` in the info string (`python illustrative`). Never present an illustrative block as the repo's code.
- **Flow sketches** (ASCII): use a `text` fence.
- Never include a code block without one of these markers. Every verbatim snippet and every `file:line` reference is checked by `scripts/check_refs.py` before you answer.
- Don't quote code in a brief explanation unless one line makes the point.

## Style

- Don't repeat the completion summary.
- Plain prose, grouped under bold or `###` headings at standard and deep depth.
- Name commit SHAs when there are any.
- Match tone, analogies and snippet length to the level in `levels.md`.
- No quizzes or exercises at this layer.
- Don't write any files.
