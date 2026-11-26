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
- [x] Uncommitted changes: before writing, the walkthrough asks whether to commit first, with a one-line reason and the files and message it would use. It commits only the session's own changes, never pushes or skips hooks; a "no" gives the existing `dirty: true` walkthrough. Scenarios 26 (no) and 31 (yes), rubric item 20
- [x] "Useful elsewhere" section in explanations, walkthroughs and code tours (`skills/explain/references/useful-elsewhere.md`): transferable gotchas, patterns and techniques, each grounded in the change, with an item limit and omitted when nothing qualifies. New *(observed)* evidence label. Walkthroughs list the items as `kompreni.lessons` in the front matter. Scenarios 32-33, rubric item 21; not yet run. The two dogfood walkthroughs predate it
- [x] Light/dark mode for rendered `.qmd` walkthroughs and code tours (`references/front-matter.md`): `theme: {light: flatly, dark: darkly}` plus `respect-user-color-scheme: true`, and a small inline `<style>` for mermaid. Left out inside an existing Quarto project. Scenarios 23, 27 and 28 updated; both dogfood walkthroughs re-rendered
    - Quarto 1.11 findings, by rendering and headless Edge screenshots in both schemes:
        - the page starts in the system scheme and follows live changes until the reader uses the toggle (then localStorage wins);
        - a standalone doc with a TOC gets a floating toggle in the top right;
        - with `darkly`, mermaid labels use `$primary` (dark blue on dark) and edges are #434343, so they are near-invisible;
        - subgraph boxes are near-black even in light mode (`--mermaid-fg-color--lightest` is derived from the body colour);
        - mermaid's own edge-label background stays light grey in dark mode;
        - the `<style>` fixes all of these through Quarto's runtime `--mermaid-*` CSS variables, so they switch with the toggle;
        - the self-contained HTML grows by about 2 MB, because both theme bundles are embedded.
    - Not tried by a reader in a real browser, only through headless screenshots. The toggle click itself was not exercised
- [x] Wider standalone walkthroughs (`references/front-matter.md`, `code-tour.md`): `grid: {sidebar-width: 0px, body-width: 1050px}` gives the body the empty left-sidebar slot; the TOC margin is unchanged. Left out inside an existing Quarto project. Scenarios 23 and 27 updated; both dogfood walkthroughs re-rendered
    - Checked by headless Edge screenshots at 1920, 1366 and 900px: the body starts at the left edge at 1366, is centred with the TOC at 1920, and collapses as before at 900. Code lines up to about 110 characters no longer clip (snapshot.py:34-42 did at 800px)
    - Trade-off: prose lines run to about 140 characters at full width, longer than the usual readable maximum. If that turns out to grate, the alternative is keeping prose at ~800px and letting code and diagrams extend left (Quarto's `column-page-left`)
- [x] Before/After tabs on every code-tour block ([HANDOVER-before-after-tabs.md](HANDOVER-before-after-tabs.md)), with changed-line tints, in all Quarto walkthroughs
    - §1 `code-tour.md` "Before and After tabs": always on for `code=all` (no argument); new files and tests stay plain; pure additions show the old lines around the insertion; an intro sentence opens the tour
    - §2 `skills/explain/scripts/before_range.py` maps After lines to old lines via `git diff -U0` hunks (shared parsing in `check_refs.diff_files`), trims blank edges, and prints `startFrom`/`changed`/`filename` for both tabs. Its mapping matched the MOOOD-study prototype's hand-made ranges on 4 blocks
    - §3 `formats.md`: tab heading level is a convention (TOC unaffected); what works inside tabs; mermaid edge labels must be quoted (a label starting with `--` errors only in the browser). SKILL.md step 7 has an optional headless-browser check for `class="error-text"`
    - §4 `check_refs.py`: Before/After tabset structure; line-mark validity (kind per side, no overlap); with `--coverage`, notes for untabbed blocks of modified files (not in callouts) and marks that disagree with the diff; dotfile paths and `./` normalised. 19 new unit tests (57 in all)
    - §5 Scenario 28 and rubric item 19 updated; scenario 27 keeps only the line-mark part of `include-in-header`
    - **Departures from the handover**: tabsets are **not linked** (`group` made the page jump when one tab switched; the checker warns about it). Lines are tinted by kind via `changed=` (yellow), `added=` (green) and `removed=` (red) in file line numbers, plus a ~20-line inline script in `include-in-header`, not the quarto-code-line-style extension. Old and new lines within a hunk are paired by `difflib` similarity (ratio >= 0.5, order-preserving DP in `check_refs.pair_lines`); paired lines are changed. In the c561b3a tour: 44 changed, 56 added, 11 removed lines, all matching in the rendered DOM. For colour-blind readers, a CSS `::after` symbol (`~`, `+`, `−`) sits in the 1em gap between Pandoc's line number and the code (checked by screenshot in both schemes; not copied, as it's generated content). The CSS `2` escape got mangled when written through a shell heredoc, so the files hold a literal U+2212
    - Extension spike (headless Edge, both schemes) *(observed)*: its `rem` hides the removed lines on a static page, its line numbers are block-relative (ignore `startFrom`), its CSS restyles every code line in the document, and it needs `_extensions/` in the user's repo (the render fails without it). The no-extension version passed every check: marks on the right lines with `startFrom`, annotation-click highlighting unaffected, one self-contained file, readable in both schemes. The parallel note [NOTE-code-line-style-extension.md](NOTE-code-line-style-extension.md) reached the same pitfalls
    - Dogfood: the c561b3a code tour has 16 new Before tabs (20 tabsets, 52 snippets), checker clean with no Before/After notes; all 35 marked blocks tint exactly the diff's lines in the rendered DOM; the key-excerpt walkthrough's one tabset was converted too
    - Not yet done: scenario 28 by a fresh agent; Before-tab annotations judged by anyone but their author; tint colours not checked for colour-blind readers (the tab name carries the meaning too)
    - §"Other findings", length bands: `code-tour.md` now says the word band covers prose outside the tour, and annotations follow the 3x-lines rule
- [ ] Pre-existing, not yet fixed: in dark mode, inline code inside code-annotation lists renders as white boxes with unreadable text (seen in the code tour, with and without the `grid` change)
- [ ] Scenarios 22-31 not yet run, in particular by a fresh agent (`claude --plugin-dir .`) with no prior context
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

- [ ] §4 Layer 3 persistent knowledge, §9 Phases 3 and 5. The walkthrough front matter is the starting point, and `kompreni.lessons` is the obvious first thing to index ("gotchas met before with this library"). Next: an index or listing across `kompreni/walkthroughs/`, and how agents find relevant walkthroughs before changing code
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
