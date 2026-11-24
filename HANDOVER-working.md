# Handover working notes

Tracks [HANDOVER-original.md](HANDOVER-original.md): what has and hasn't been actioned.

## Done (Layer 1, v0.1.0)

- [x] §4 Layer 1 conversational explanation skill: `skills/explain/`
- [x] §5 Skills: packaged as a plugin (`.claude-plugin/`), invoked as `/kompreni:explain`
- [x] §7 Design principles built into the skill: proportionality, evidence labels, provenance, no forced files, portable (plain SKILL.md, no scripts)
- [x] §7 Evidence-based / provenance: snippet rules plus `scripts/check_refs.py` (checks references and verbatim snippets; tested on a scratch repo only)
- [x] History mode: `branch=`, `since=`, `commit=` (`references/history-mode.md`). This answers §10 Q4 in part: what can be reconstructed afterwards from git and PRs, as groundwork for Layer 3
- [x] Unit tests for `check_refs.py` (`tests/`)
- [x] §7 Support learning and retention: prior-knowledge levels (`references/levels.md`) and a "Concepts used here" section
- [x] §9 Phase 1 scaffolding: skill, examples, eval scenarios

## In progress / not yet verified

- [ ] §9 Phase 1: "Test this on several different types of changes": the 8 scenarios in `evals/scenarios/` are written but **not yet run**
- [ ] Check the frontmatter fields and `$ARGUMENTS` handling against current Claude Code skill docs
- [ ] Run `claude plugin validate .`
- [ ] Dogfood on a real session
- [ ] History mode: run on `C:\geographic_playground_mini` (dry run of the git/gh commands done: default-branch fallback via `gh` works; `review-fixes` is merged as PR #2, merge commit `423fc80`; `stlite` has no commits beyond main) and scenarios 09-13; no full skill run yet
- [ ] Check that agents actually run `check_refs.py` via the stdin heredoc in real sessions (long drafts, Windows quoting)
- [ ] `check_refs.py` can't verify claims about behaviour, only that quoted code and references exist

## Deferred

- [ ] §4 Layer 2 structured walkthroughs (Quarto)
- [ ] §4 Layer 3 persistent knowledge, §9 Phases 3 and 5
- [x] §5 / §9 Phase 4 first mod: `mods/kompreni-offer` (detect a turn with edits, offer an explanation, fill the command). Validated, type-checked and unit-tested; **not yet tried in a live session or in VS Code**
- [ ] Mods: richer UI (a pane listing changed files, per-file explain), capture of Bash-made changes (e.g. a git snapshot per turn), access to earlier explanations
- [ ] §5 Other agent integrations
- [ ] §8 Name availability check (GitHub, registries, domains, trademark)
- [ ] Link to codebase-tutorial: flag chapters made stale by a change (via `_generation.json`)
- [ ] History mode: `range=<A..B>` (raw git syntax) and `pr=<number>` (explain a PR directly, e.g. after a squash merge and branch deletion)
- [ ] Levels: scenarios 14-17 not yet run. Possible later additions: a `knows=<language>` argument if free text is used a lot; a codebase-familiarity axis (new to this repo vs new to the language); a `.kompreni.yml` for a default level
- [ ] A change-collection script, only if scenarios show inline git steps are unreliable

## Open questions (§10)

Q10 (simplest MVP) is answered by this layer. The rest wait on Layers 2-3.
