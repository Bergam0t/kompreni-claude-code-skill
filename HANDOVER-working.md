# Handover working notes

Tracks [HANDOVER-original.md](HANDOVER-original.md): what has and hasn't been actioned.

## Done (Layer 1, v0.1.0)

- [x] §4 Layer 1 conversational explanation skill: `skills/explain/`
- [x] §5 Skills: packaged as a plugin (`.claude-plugin/`), invoked as `/kompreni:explain`
- [x] §7 Design principles built into the skill: proportionality, evidence labels, provenance, no forced files, portable (plain SKILL.md, no scripts)
- [x] §7 Evidence-based / provenance: snippet rules plus `scripts/check_refs.py` (checks references and verbatim snippets; tested on a scratch repo only)
- [x] §9 Phase 1 scaffolding: skill, examples, eval scenarios

## In progress / not yet verified

- [ ] §9 Phase 1: "Test this on several different types of changes": the 8 scenarios in `evals/scenarios/` are written but **not yet run**
- [ ] Check the frontmatter fields and `$ARGUMENTS` handling against current Claude Code skill docs
- [ ] Run `claude plugin validate .`
- [ ] Dogfood on a real session
- [ ] Check that agents actually run `check_refs.py` via the stdin heredoc in real sessions (long drafts, Windows quoting)
- [ ] `check_refs.py` can't verify claims about behaviour, only that quoted code and references exist

## Deferred

- [ ] §4 Layer 2 structured walkthroughs (Quarto)
- [ ] §4 Layer 3 persistent knowledge, §9 Phases 3 and 5
- [ ] §5 Claude Code mods and hooks, §9 Phase 4
- [ ] §5 Other agent integrations
- [ ] §8 Name availability check (GitHub, registries, domains, trademark)
- [ ] Link to codebase-tutorial: flag chapters made stale by a change (via `_generation.json`)
- [ ] A change-collection script, only if scenarios show inline git steps are unreliable

## Open questions (§10)

Q10 (simplest MVP) is answered by this layer. The rest wait on Layers 2-3.
