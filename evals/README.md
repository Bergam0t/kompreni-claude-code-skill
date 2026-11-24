# Evals

Manual scenarios for checking `/kompreni:explain`. Each file in `scenarios/` describes a throwaway repo setup, the task to give Claude, and what a good explanation must show.

## Running a scenario

1. Create the repo in a scratch folder as the scenario says, and `git init` it.
2. Run `claude --plugin-dir <this project>` there and give the task.
3. Run `/kompreni:explain` (add arguments if the scenario says).
4. Score the output against the rubric below, and compare it with the agent's own completion summary.

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
10. Beats the completion summary on understanding

## Results

None recorded yet.
