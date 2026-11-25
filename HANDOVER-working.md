# Handover working notes

Tracks [HANDOVER-original.md](HANDOVER-original.md): what has and hasn't been actioned.

## Done (Layer 1, v0.1.0)

- [x] §4 Layer 1 conversational explanation skill: `skills/explain/`
- [x] §5 Skills: packaged as a plugin (`.claude-plugin/`), invoked as `/kompreni:explain`
- [x] §7 Design principles built into the skill: proportionality, evidence labels, provenance, no forced files, portable (plain SKILL.md, no scripts)
- [x] §7 Evidence-based / provenance: snippet rules plus `scripts/check_refs.py` (checks references and verbatim snippets; tested on a scratch repo only)
- [x] History mode: `branch=`, `since=`, `commit=` (`references/history-mode.md`). This answers §10 Q4 in part: what can be reconstructed afterwards from git and PRs, as groundwork for Layer 3
- [x] Unit tests for `check_refs.py` (`tests/`)
- [x] Repeated explanations: `scope=new|all`, with git-tree snapshots (`scripts/snapshot.py`, tested) so each explanation covers only what's new. Partly answers §10 Q1 (a complete, reliable account of changes): snapshots catch shell-made changes that edit events miss. Fixed: the index copy lost its mtime, so on Git for Windows (which compares mtimes to the second) a same-size edit in the same second could be left out; there is now a deterministic test for it
- [x] §7 Support learning and retention: prior-knowledge levels (`references/levels.md`) and a "Concepts used here" section
- [x] §9 Phase 1 scaffolding: skill, examples, eval scenarios

## Layer 2: structured walkthroughs (§4, §9 Phase 2)

- [x] `/kompreni:walkthrough` (`skills/walkthrough/`). It reuses explain's collection, grouping, levels, history mode and scripts by path, and writes `kompreni/walkthroughs/<date>-<slug>.{qmd,md}`
- [x] Markdown versus Quarto: `.qmd` by default when Quarto is available, GFM `.md` otherwise (`references/formats.md`). Both share one structure
- [x] Document structure, annotated code, diagrams, before/after and learning questions (`references/structure.md`). This partly answers §10 Q6 (educational rather than verbose): problem first, one running example traced before and after, diagrams only when the flow changed, optional depth collapsed, checked answers. It also partly answers Q7 (Quarto without complexity): a single file rendered to one self-contained HTML, no project, no extensions
- [x] "When is a full walkthrough worthwhile": a proportionality gate. Brief-sized changes get the suggestion to use explain instead, and the user is asked before anything is written. Standard-sized changes get a short walkthrough, deep ones a full one
- [x] Front matter `kompreni:` (schema 1) as the seed of the Phase 3 knowledge format (`references/front-matter.md`)
- [x] `check_refs.py` handles Quarto blocks, front matter and GitHub permalinks. Unit tested
- [x] Dogfood: `commit=c561b3a`. The output is `kompreni/walkthroughs/2026-11-24-explain-only-new-changes.qmd`
    - It renders cleanly and the checker passes
    - The checker caught one wrong line range. A wrong path in prose with no line number was found only by re-reading
    - A GFM conversion of it also passes the checker; GitHub rendering itself is unchecked
    - Caveat: written by the same agent that wrote the skill, so it's not an independent test
- [x] Code tours: `code=all` (`references/code-tour.md`). All the substantive changed code, annotated line by line with Quarto code annotations (`below`), with real line numbers via `.numberLines startFrom=`
    - Quarto 1.11 findings, by rendering (not in Quarto's docs):
        - a second paragraph in an annotation item is silently dropped;
        - prose between a block and its list silently unlinks the annotations;
        - an item starting like a list (`- `, `a. `, a bare `A.`) crashes the whole render;
        - `<!-- <n> -->` works in Markdown blocks, `/* <n> */` in CSS;
        - `startFrom` works alongside `filename`, and the highlights use the real line numbers.
    - `check_refs.py`: annotation integrity, `startFrom`, and `--coverage BASE[..TIP]`
    - Dogfood: `kompreni/walkthroughs/2026-11-25-explain-only-new-changes-code-tour.qmd`. 36 annotated blocks; every annotation's highlighted lines were verified against the HTML
- [x] §9 Phase 4 "allow the user to request a Quarto walkthrough": Walkthrough and Code tour buttons in `kompreni-offer` (mod 0.1.3). A session-mode walkthrough resets the count. Tests pass (`claude plugin test`); **not tried live**, and not type-checked (no `tsc` here, and the API types are only written when Claude Code loads the mod)
- [ ] Scenarios 22-30 not yet run, in particular by a fresh agent (`claude --plugin-dir .`) with no prior context
- [ ] Code tours of large changes (the 600-line rule) not yet tried
- [ ] A code tour's teaching value not yet judged by anyone but its author
- [ ] GFM output not yet viewed on GitHub (alerts, mermaid, `<details>`)
- [ ] Quarto quirk to remember: inside an existing Quarto project, `quarto render <file>` writes into the project's output dir, and website projects pick up `kompreni/walkthroughs/` on their next full render. `render=auto` skips rendering there and says so

## In progress / not yet verified

- [ ] §9 Phase 1: "Test this on several different types of changes": the 8 scenarios in `evals/scenarios/` are written but **not yet run**
- [ ] Check the frontmatter fields and `$ARGUMENTS` handling against current Claude Code skill docs
- [ ] Run `claude plugin validate .`
- [ ] Dogfood on a real session
- [ ] History mode: run on `C:\geographic_playground_mini` (dry run of the git/gh commands done: default-branch fallback via `gh` works; `review-fixes` is merged as PR #2, merge commit `423fc80`; `stlite` has no commits beyond main) and scenarios 09-13; no full skill run yet
- [ ] Check that agents actually run `check_refs.py` via the stdin heredoc in real sessions (long drafts, Windows quoting)
- [ ] `check_refs.py` can't verify claims about behaviour, only that quoted code and references exist

## Deferred

- [ ] §4 Layer 3 persistent knowledge, §9 Phases 3 and 5. The walkthrough front matter is the starting point. Next: an index or listing across `kompreni/walkthroughs/`, and how agents find relevant walkthroughs before changing code
- [ ] Walkthroughs: re-pin a `dirty: true` walkthrough to a SHA after commit; interactive exercises beyond collapsed Q&A
- [x] §5 / §9 Phase 4 first mod: `mods/kompreni-offer` (an Explain row above the prompt, shown always by default or only after turns with edits via `show=changes`; fills the command). Validated, type-checked and unit-tested; **not yet tried in a live session or in VS Code**
- [ ] Mods: richer UI (a pane listing changed files, per-file explain), capture of Bash-made changes (e.g. a git snapshot per turn), access to earlier explanations
- [ ] §5 Other agent integrations
- [ ] §8 Name availability check (GitHub, registries, domains, trademark)
- [ ] Link to codebase-tutorial: flag chapters made stale by a change (via `_generation.json`)
- [ ] History mode: `range=<A..B>` (raw git syntax) and `pr=<number>` (explain a PR directly, e.g. after a squash merge and branch deletion)
- [ ] Levels: scenarios 14-17 not yet run. Possible later additions: a `knows=<language>` argument if free text is used a lot; a codebase-familiarity axis (new to this repo vs new to the language); a `.kompreni.yml` for a default level
- [ ] Scenarios 18-21 (repeated explanations) not yet run
- [ ] A change-collection script, only if scenarios show inline git steps are unreliable

## Open questions (§10)

Q10 (simplest MVP) is answered by Layer 1. Q6 and Q7 are partly answered by Layer 2 (see above), pending scenario runs. Q8 (persistent format) has a first draft in the walkthrough front matter. Q9 waits on Layer 3.
