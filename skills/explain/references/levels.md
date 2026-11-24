# Prior-knowledge levels

The level sets how much the explanation teaches the **language and its ecosystem** (constructs, idioms, libraries, patterns) alongside the change itself. It doesn't change what is explained about the change, only how much background the reader is given to follow it.

## Choosing the level

1. If `level=` was given, use it. `beginner` is an alias for `new-to-programming`, the same meaning as in codebase-tutorial.
2. Otherwise, use what the user has said about their experience: in this conversation, in `CLAUDE.md`, or in your memory ("I'm new to Python", "I mostly write R"). Map it to a preset, or treat it as free text.
3. Otherwise, use `intermediate`.

State the level in the opening line alongside the depth, e.g. "Depth: standard. Level: new-to-language (from your note that you're new to Python).", so the user can correct it.

If the diff spans several languages, apply the level to each. A free-text level can differ per language ("expert in SQL, new to Python").

## Presets

### `new-to-programming` (alias `beginner`)

- **Reader**: new to programming in general, as well as to this language.
- **Explain**: general programming concepts the change relies on (functions and arguments, loops, conditionals, classes and objects, exceptions, state and mutation, what a test does), and every language construct needed to follow the change.
- **Tone**: welcoming and plain. Define every technical term the first time it appears. Never imply something "should" be known.
- **Analogies**: use them freely, with concrete everyday examples.
- **Code**: short excerpts (about 8 lines at most). Follow each with a plain line-by-line reading of what it does. Trace one concrete example through the change step by step where that helps.
- **Concepts section**: up to 5 concepts.

### `new-to-language`

- **Reader**: an experienced programmer who is new to this language (or its main libraries).
- **Explain**: the language's syntax and idioms, surprising semantics, conventions and key library APIs that appear in the change. Map each one onto a general concept the reader already knows: "a decorator is a function that wraps another function, applied where it's defined". Point out gotchas that would trip up someone coming from another language: truthiness, mutable default arguments, late binding in closures, `==` vs `is`, 0- vs 1-based indexing, copy vs view.
- **Don't explain**: programming basics (loops, functions, classes, what a test is). That would be patronising.
- **Tone**: direct, peer to peer.
- **Analogies**: rarely. Prefer "this is the language's version of X".
- **Code**: normal excerpt lengths. Explain the idiomatic parts, not every line.
- **Concepts section**: up to 5 concepts.

### `intermediate` (default)

- **Reader**: comfortable in the language, but may not know every idiom or library.
- **Explain**: only less-common language features, non-obvious library behaviour, and project-specific patterns, briefly.
- **Tone**: readable, not patronising.
- **Analogies**: only for genuinely complex ideas.
- **Concepts section**: up to 3 concepts, and only if something qualifies. Often there is none.

### `advanced`

- **Reader**: experienced in the language and its ecosystem.
- **Explain**: no language or library background. Spend the words on design, invariants, interactions and risks.
- **Tone**: concise, peer to peer.
- **Analogies**: none, unless one clarifies a non-obvious concurrency or ownership model.
- **Concepts section**: none. A project-specific convention the change relies on can still be named in one line under "What changed".

### Free text

Example: `level="fluent in R, new to Python"`. Follow the closest preset (here `new-to-language`) and **explain new constructs by comparison with what the reader knows**: a list comprehension next to `lapply`/`purrr::map`, pandas `groupby().agg()` next to `dplyr::group_by() |> summarise()`, 0-based indexing against R's 1-based. Only make a comparison you're sure is accurate. If no close equivalent exists, say so in a few words rather than forcing one.

## The "Concepts used here" section

For every level except `advanced`, when the change uses something the reader likely doesn't know, add **Concepts used here** before "What changed". It covers four kinds of thing, but only where they occur in this change:
- language constructs (generators, decorators, `async`/`await`, context managers, type hints);
- design patterns (a registry, dependency injection, caching, a callback);
- library and framework APIs (Streamlit `st.session_state`, pandas `merge`);
- project-specific conventions the change follows.

For each concept, write:
- **What it is**, in one or two sentences at the reader's level.
- **Where it appears**, as a real `file:line` reference (checked by `check_refs.py` like any other), and, if it helps, a short verbatim excerpt.
- **Why it's used here**: what it does for this change specifically.

Rules:
- **Pick the concepts the reader needs in order to follow the change**, up to the preset's limit. Leave out the rest; this isn't a language tutorial. If more qualify than fit, say so in one line ("Also used: X, Y").
- **General facts must be accurate.** These describe the language, not the repo, so they need no evidence label. Behaviour that depends on the version (a language version, a library version) should be named with the version, or not stated.
- **Explain a concept once.** Later sections can refer back by name.
- At `depth=brief`, there is no section. Instead, give a one-line gloss in parentheses at the concept's first mention, for at most two concepts.
- The section's words don't count towards the depth's word limit.
