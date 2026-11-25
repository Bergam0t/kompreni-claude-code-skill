# Evals

Manual scenarios for checking `/kompreni:explain` and `/kompreni:walkthrough`. Each file in `scenarios/` describes a throwaway repo setup, the task to give Claude, and what a good explanation must show.

## Running a scenario

1. Create the repo in a scratch folder as the scenario says, and `git init` it.
2. Run `claude --plugin-dir <this project>` there and give the task.
3. Run `/kompreni:explain` (add arguments if the scenario says).
4. Score the output against the rubric below, and compare it with the agent's own completion summary.

Scenarios 09-13 test history mode. They need a repo with branches and commits set up first; the chat history doesn't matter, except in 13.

Scenarios 22-29 and 31 test walkthroughs. Score them on rubric items 1-13 as well as 15-21, reading the written file rather than the chat reply. Scenario 30 tests the mod's walkthrough buttons. Scenarios 32-33 test the "Useful elsewhere" section (rubric item 21, which also applies to every other scenario).

## Rubric (pass / partial / fail each)

1. Grouped by purpose, not file
2. Before and after behaviour is clear
3. Interactions with existing code are explained
4. Rationale carries evidence labels, with nothing invented
5. Verification is honest (no claimed test runs that didn't happen)
6. Length is proportionate to the change
7. File and line references are accurate (spot-check by hand, not only with the script)
8. Quoted code is real: verbatim snippets match the repo, anything else is marked `illustrative`
9. The agent ran `check_refs.py` and fixed what it reported (or said it couldn't)
10. Beats the completion summary on understanding (history mode: beats reading `git log` and the diff)
11. History mode: the scope is correct (the right range, no changes merged in from main, uncommitted work excluded) and nothing in the checkout changed
12. History mode: reasons from commits and PRs are labelled *(commit)* or *(PR #n)*, and agent-written commit summaries aren't presented as reasons
13. Level: the concepts explained fit the level (no programming basics for `new-to-language`, none at all for `advanced`), are accurate, cite real lines, and stay within the limit
14. Repeated explanations: a second explanation covers only what's new, says how it interacts with what was explained before, and ends with a valid snapshot line
15. Walkthrough: it stands alone for a reader who wasn't in the conversation (no "as discussed", no quoted chat, no personal details)
16. Walkthrough: it teaches rather than pads: the problem comes first, one running example is traced before and after, diagrams and annotated excerpts earn their place, and length is within the band
17. Walkthrough: the questions are answerable from the document, and every answer matches the code
18. Walkthrough: the file is in the right place with the right name, `check_refs.py` passes on it, a `qmd` renders with no warnings (or rendering was skipped for a stated reason), and the front matter is complete with correct SHAs and file list
19. Code tour (`code=all`): every substantive changed line is shown or listed as not toured (check with `--coverage`); annotations say why, not just what; line numbers match the files; tests are annotated inside collapsed callouts
20. Walkthrough of uncommitted changes: it asks once, briefly, whether to commit first, before writing anything. On yes it commits only the session's changes, runs hooks and doesn't push; on no it writes with the drift note and doesn't ask again
21. Useful elsewhere: every item is tied to this change (a line, an error seen, a commit or PR), would help on other code, is accurate (check library claims against the docs) and is labelled; no generic advice; within the item limit; left out when nothing qualifies. In a walkthrough, the items match `kompreni.lessons`

Unit tests for the checker: `python -m unittest discover tests`.

## Results

- 2026-11-24, walkthrough dogfood, `/kompreni:walkthrough commit=c561b3a` on this repo. Output: [`kompreni/walkthroughs/2026-11-24-explain-only-new-changes.qmd`](../kompreni/walkthroughs/2026-11-24-explain-only-new-changes.qmd). Not independent: it was written by the agent that wrote the skill.
    - Item 18 passes: the checker passes with `--ref c561b3a`, after it caught one wrong range; `quarto render` gives no warnings; the HTML is ignored by git; the front matter SHAs were taken from `git rev-parse`.
    - Item 7 is partial: one wrong path in prose (no line number) wasn't caught by the checker and was found on re-reading.
    - Items 15-17 have not been scored independently.
- 2026-11-25, code tour dogfood, `/kompreni:walkthrough commit=c561b3a code=all`. Output: [`kompreni/walkthroughs/2026-11-25-explain-only-new-changes-code-tour.qmd`](../kompreni/walkthroughs/2026-11-25-explain-only-new-changes-code-tour.qmd). Not independent either.
    - 36 annotated blocks. The checker found one snippet missing its last line, which was then fixed.
    - Coverage: all 30 remaining notes are in files listed as not toured.
    - The render is clean, and a script confirmed that every annotation targets exactly the lines carrying its marker.
    - Item 19 passes on the mechanics; how well the annotations teach hasn't been judged by anyone else.
